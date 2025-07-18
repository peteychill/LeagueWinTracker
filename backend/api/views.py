from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .serializers import (
    UserSerializer, UserProfileSerializer, FriendSerializer, 
    MatchSerializer, AnalysisTileSerializer, RegisterSerializer, RiotIdSerializer
)
from .riot_api import RiotAPIService, RiotAPIError
from core.models import Friend, Match, MatchParticipant, AnalysisTile, UserProfile


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Log the user in after successful registration
            login(request, user)
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data
            })
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


class UserProfileView(APIView):
    def get(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    def put(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendListView(generics.ListCreateAPIView):
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Friend.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        import logging
        logger = logging.getLogger(__name__)
        
        # Get Riot ID from request
        riot_id = self.request.data.get('riot_id')
        region = self.request.data.get('region', 'na1')
        
        logger.info(f"FriendListView: Adding friend with Riot ID: {riot_id}, region: {region}")
        
        if not riot_id:
            logger.error("FriendListView: Riot ID is required")
            raise ValueError("Riot ID is required")
        
        try:
            # Use Riot API to get summoner info
            logger.info(f"FriendListView: Fetching summoner data for {riot_id}")
            riot_service = RiotAPIService()
            summoner_data = riot_service.get_summoner_by_riot_id(riot_id, region)
            logger.info(f"FriendListView: Summoner data received: {summoner_data}")
            
            # Create friend with API data
            friend = serializer.save(
                user=self.request.user,
                puuid=summoner_data['puuid'],
                summoner_name=summoner_data['gameName'],
                tag_line=summoner_data['tagLine'],
                region=region
            )
            logger.info(f"FriendListView: Friend created successfully: {friend}")
        except RiotAPIError as e:
            logger.error(f"FriendListView: Riot API error: {e}")
            raise ValueError(f"Failed to fetch summoner data: {e}")
        except Exception as e:
            logger.error(f"FriendListView: Unexpected error: {e}")
            raise


class FriendDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Friend.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Update friend and optionally refresh match data"""
        import logging
        logger = logging.getLogger(__name__)
        
        friend = self.get_object()
        match_count = request.data.get('match_count')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')
        
        # Update friend fields if provided
        if match_count is not None:
            friend.match_count = match_count
        if date_from is not None:
            friend.date_from = date_from
        if date_to is not None:
            friend.date_to = date_to
        
        # If any match-related fields were updated, refresh matches
        if any([match_count is not None, date_from is not None, date_to is not None]):
            try:
                friend.save()
                
                # Refresh matches with new parameters
                riot_service = RiotAPIService()
                
                if date_from or date_to:
                    # Use date range query
                    match_ids = riot_service.get_match_ids_by_date_range(
                        friend.puuid, 
                        friend.region, 
                        date_from=friend.date_from,
                        date_to=friend.date_to,
                        count=friend.match_count
                    )
                else:
                    # Use regular recent matches query
                    match_ids = riot_service.get_match_ids(friend.puuid, friend.region, count=friend.match_count)
                
                new_matches = 0
                with transaction.atomic():
                    for match_id in match_ids:
                        # Check if match already exists
                        if Match.objects.filter(match_id=match_id).exists():
                            continue
                        
                        # Get match details
                        match_data = riot_service.get_match_details(match_id, friend.region)
                        match_info, participants_data = riot_service.parse_match_data(match_data)
                        
                        # Create match
                        match_obj = Match.objects.create(**match_info)
                        
                        # Create participants
                        for participant_data in participants_data:
                            MatchParticipant.objects.create(
                                match=match_obj,
                                **participant_data
                            )
                        
                        new_matches += 1
                
                # Update total matches fetched (add to existing total, don't replace)
                friend.total_matches_fetched += new_matches
                friend.save()
                
                logger.info(f"Refreshed {new_matches} new matches for friend {friend.summoner_name} (total: {friend.total_matches_fetched})")
                
                # Return the updated friend data
                serializer = self.get_serializer(friend)
                return Response(serializer.data)
                
            except Exception as e:
                logger.error(f"Error refreshing matches for friend {friend.summoner_name}: {e}")
                return Response({
                    'error': f'Failed to refresh matches: {e}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # If no match-related fields provided, use the default update behavior
        return super().update(request, *args, **kwargs)


class MatchListView(generics.ListAPIView):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Match.objects.all()


class RefreshMatchesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, puuid):
        try:
            riot_service = RiotAPIService()
            
            # Get recent match IDs
            match_ids = riot_service.get_match_ids(puuid, count=20)
            
            new_matches = 0
            with transaction.atomic():
                for match_id in match_ids:
                    # Check if match already exists
                    if Match.objects.filter(match_id=match_id).exists():
                        continue
                    
                    # Get match details
                    match_data = riot_service.get_match_details(match_id)
                    match_info, participants_data = riot_service.parse_match_data(match_data)
                    
                    # Create match
                    match_obj = Match.objects.create(**match_info)
                    
                    # Create participants
                    for participant_data in participants_data:
                        MatchParticipant.objects.create(
                            match=match_obj,
                            **participant_data
                        )
                    
                    new_matches += 1
            
            # Update user profile last sync time
            if hasattr(request.user, 'profile'):
                request.user.profile.last_match_sync = timezone.now()
                request.user.profile.save()
            
            return Response({
                'message': f'Successfully refreshed {new_matches} new matches',
                'new_matches': new_matches
            })
            
        except RiotAPIError as e:
            return Response({
                'error': f'Failed to refresh matches: {e}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Unexpected error: {e}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalysisTileListView(generics.ListCreateAPIView):
    serializer_class = AnalysisTileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnalysisTile.objects.filter(user=self.request.user).prefetch_related('friends')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnalysisTileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnalysisTileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnalysisTile.objects.filter(user=self.request.user).prefetch_related('friends')


class TileMatchesView(generics.ListAPIView):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        tile = get_object_or_404(AnalysisTile, id=self.kwargs['pk'], user=self.request.user)
        # Use the tile's max_matches_per_tile setting
        return tile.get_filtered_matches(limit=tile.max_matches_per_tile)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def test_riot_api(request):
    """Test Riot API connection"""
    try:
        riot_service = RiotAPIService()
        test_result = riot_service.test_api_connection()
        return Response(test_result)
    except Exception as e:
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_friend_by_riot_id(request):
    """Add a friend by Riot ID using the Riot API"""
    import logging
    logger = logging.getLogger(__name__)
    
    serializer = RiotIdSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    riot_id = serializer.validated_data['riot_id']
    region = serializer.validated_data['region']
    match_count = request.data.get('match_count', settings.DEFAULT_MATCH_COUNT)
    date_from = request.data.get('date_from')
    date_to = request.data.get('date_to')
    
    logger.info(f"Adding friend: {riot_id} in region {region} with {match_count} matches")
    if date_from or date_to:
        logger.info(f"Date range: {date_from} to {date_to}")
    
    try:
        riot_service = RiotAPIService()
        logger.info(f"Fetching summoner data for {riot_id}")
        summoner_data = riot_service.get_summoner_by_riot_id(riot_id, region)
        logger.info(f"Summoner data received: {summoner_data}")
        
        # Check if friend already exists
        if Friend.objects.filter(user=request.user, puuid=summoner_data['puuid']).exists():
            return Response({
                'error': 'Friend already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create friend
        friend = Friend.objects.create(
            user=request.user,
            riot_id=riot_id,
            puuid=summoner_data['puuid'],
            summoner_name=summoner_data['gameName'],
            tag_line=summoner_data['tagLine'],
            region=region,
            match_count=match_count,
            date_from=date_from,
            date_to=date_to
        )
        logger.info(f"Friend created: {friend}")
        
        # Automatically fetch match data for the new friend
        try:
            if date_from or date_to:
                logger.info(f"Fetching {match_count} match IDs for PUUID: {summoner_data['puuid']} with date range")
                match_ids = riot_service.get_match_ids_by_date_range(
                    summoner_data['puuid'], 
                    region, 
                    date_from=date_from,
                    date_to=date_to,
                    count=match_count
                )
            else:
                logger.info(f"Fetching {match_count} match IDs for PUUID: {summoner_data['puuid']}")
                match_ids = riot_service.get_match_ids(summoner_data['puuid'], region, count=match_count)
            
            logger.info(f"Found {len(match_ids)} match IDs")
            
            new_matches = 0
            
            with transaction.atomic():
                for i, match_id in enumerate(match_ids):
                    logger.info(f"Processing match {i+1}/{len(match_ids)}: {match_id}")
                    
                    # Check if match already exists
                    if Match.objects.filter(match_id=match_id).exists():
                        logger.info(f"Match {match_id} already exists, skipping")
                        continue
                    
                    # Get match details
                    logger.info(f"Fetching match details for {match_id}")
                    match_data = riot_service.get_match_details(match_id, region)
                    match_info, participants_data = riot_service.parse_match_data(match_data)
                    logger.info(f"Match {match_id} has {len(participants_data)} participants")
                    
                    # Create match
                    match_obj = Match.objects.create(**match_info)
                    
                    # Create participants
                    for participant_data in participants_data:
                        MatchParticipant.objects.create(
                            match=match_obj,
                            **participant_data
                        )
                    
                    new_matches += 1
                    logger.info(f"Successfully created match {match_id}")
            
            # Update total matches fetched
            friend.total_matches_fetched = new_matches
            friend.save()
            
            logger.info(f"Successfully processed {new_matches} new matches")
            return Response({
                'friend': FriendSerializer(friend).data,
                'new_matches': new_matches
            })
            
        except Exception as match_error:
            logger.error(f"Error fetching matches: {match_error}")
            # If match fetching fails, still return the friend but with a warning
            return Response({
                'friend': FriendSerializer(friend).data,
                'message': f'Friend added successfully, but failed to fetch match data: {match_error}',
                'new_matches': 0
            }, status=status.HTTP_201_CREATED)
        
    except RiotAPIError as e:
        logger.error(f"Riot API error: {e}")
        return Response({
            'error': f'Failed to fetch summoner data: {e}'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return Response({
            'error': f'Unexpected error: {e}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 