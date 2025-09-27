from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Friend, Match, MatchParticipant, AnalysisTile, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'riot_id', 'puuid', 'summoner_name', 'tag_line', 'region', 'last_match_sync']


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['id', 'riot_id', 'puuid', 'summoner_name', 'tag_line', 'region', 'match_count', 'date_from', 'date_to', 'total_matches_fetched', 'created_at']
        read_only_fields = ['id', 'created_at']


class MatchParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchParticipant
        fields = [
            'puuid', 'summoner_name', 'champion_id', 'champion_name', 
            'team_id', 'win', 'kills', 'deaths', 'assists', 
            'gold_earned', 'total_damage_dealt', 'total_damage_taken', 
            'vision_score', 'cs', 'role', 'lane'
        ]


class MatchSerializer(serializers.ModelSerializer):
    participants = MatchParticipantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id', 'match_id', 'game_mode', 'game_type', 'queue_id',
            'game_duration', 'game_creation', 'platform_id', 'participants'
        ]


class AnalysisTileSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True, read_only=True)
    friend_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    win_rate = serializers.ReadOnlyField()
    wins = serializers.ReadOnlyField()
    losses = serializers.ReadOnlyField()
    total_matches = serializers.ReadOnlyField()
    
    class Meta:
        model = AnalysisTile
        fields = ['id', 'name', 'friends', 'friend_ids', 'match_filter', 'date_from', 'date_to', 'max_matches_per_tile', 'win_rate', 'wins', 'losses', 'total_matches', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def to_internal_value(self, data):
        """Convert empty strings to None for date fields"""
        if 'date_from' in data and data['date_from'] == '':
            data['date_from'] = None
        if 'date_to' in data and data['date_to'] == '':
            data['date_to'] = None
        return super().to_internal_value(data)
    
    def validate(self, data):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"AnalysisTileSerializer: Starting validation with data: {data}")
        
        # Check if name is provided
        if not data.get('name'):
            logger.error("AnalysisTileSerializer: Name is required but not provided")
            raise serializers.ValidationError("Name is required")
        
        # Check if friend_ids is provided and not empty
        friend_ids = data.get('friend_ids', [])
        if not friend_ids:
            logger.error("AnalysisTileSerializer: At least one friend must be selected")
            raise serializers.ValidationError("At least one friend must be selected")
        
        # Validate date format if provided (dates are now None if empty strings were passed)
        date_from = data.get('date_from')
        if date_from is not None:
            try:
                from datetime import datetime
                # Check if it's already a date object or a string
                if isinstance(date_from, str):
                    datetime.strptime(date_from, '%Y-%m-%d')
                # If it's already a date object, it's valid
            except ValueError:
                logger.error("AnalysisTileSerializer: Invalid date_from format")
                raise serializers.ValidationError("date_from must be in YYYY-MM-DD format")
        
        date_to = data.get('date_to')
        if date_to is not None:
            try:
                from datetime import datetime
                # Check if it's already a date object or a string
                if isinstance(date_to, str):
                    datetime.strptime(date_to, '%Y-%m-%d')
                # If it's already a date object, it's valid
            except ValueError:
                logger.error("AnalysisTileSerializer: Invalid date_to format")
                raise serializers.ValidationError("date_to must be in YYYY-MM-DD format")
        
        logger.info(f"AnalysisTileSerializer: Validation passed for name: {data.get('name')} and friend_ids: {friend_ids}")
        return data
    
    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"AnalysisTileSerializer: Starting create with validated_data: {validated_data}")
        
        friend_ids = validated_data.pop('friend_ids', [])
        logger.info(f"AnalysisTileSerializer: Extracted friend_ids: {friend_ids}")
        
        # Handle empty string dates
        if 'date_from' in validated_data and validated_data['date_from'] == '':
            validated_data['date_from'] = None
            logger.info("AnalysisTileSerializer: Converted empty date_from to None")
        if 'date_to' in validated_data and validated_data['date_to'] == '':
            validated_data['date_to'] = None
            logger.info("AnalysisTileSerializer: Converted empty date_to to None")
        
        logger.info(f"AnalysisTileSerializer: Final validated_data for tile creation: {validated_data}")
        
        try:
            tile = AnalysisTile.objects.create(**validated_data)
            logger.info(f"AnalysisTileSerializer: Tile created with ID: {tile.id}")
            
            if friend_ids:
                friends = Friend.objects.filter(id__in=friend_ids, user=self.context['request'].user)
                logger.info(f"AnalysisTileSerializer: Found {friends.count()} friends for IDs: {friend_ids}")
                tile.friends.set(friends)
                logger.info(f"AnalysisTileSerializer: Friends set successfully")
            else:
                logger.info("AnalysisTileSerializer: No friend_ids provided")
            
            return tile
        except Exception as e:
            logger.error(f"AnalysisTileSerializer: Error creating tile: {str(e)}")
            raise
    
    def update(self, instance, validated_data):
        friend_ids = validated_data.pop('friend_ids', None)
        
        # Handle empty string dates
        if 'date_from' in validated_data and validated_data['date_from'] == '':
            validated_data['date_from'] = None
        if 'date_to' in validated_data and validated_data['date_to'] == '':
            validated_data['date_to'] = None
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if friend_ids is not None:
            friends = Friend.objects.filter(id__in=friend_ids, user=self.context['request'].user)
            instance.friends.set(friends)
        
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class RiotIdSerializer(serializers.Serializer):
    riot_id = serializers.CharField(max_length=100)
    region = serializers.CharField(max_length=10, default='na1') 