from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Friend(models.Model):
    """Represents a friend that a user wants to track"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
    riot_id = models.CharField(max_length=100, help_text="Riot ID (e.g., 'SummonerName#TAG')")
    puuid = models.CharField(max_length=100, help_text="Riot PUUID")
    summoner_name = models.CharField(max_length=100)
    tag_line = models.CharField(max_length=10)
    region = models.CharField(max_length=10, default='na1')
    match_count = models.IntegerField(default=50, help_text="Number of matches to fetch")
    date_from = models.DateField(null=True, blank=True, help_text="Start date for match query (YYYY-MM-DD)")
    date_to = models.DateField(null=True, blank=True, help_text="End date for match query (YYYY-MM-DD)")
    total_matches_fetched = models.IntegerField(default=0, help_text="Total number of matches fetched for this friend")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'puuid']
        ordering = ['summoner_name']

    def __str__(self):
        return f"{self.summoner_name}#{self.tag_line}"


class Match(models.Model):
    """Represents a League of Legends match"""
    match_id = models.CharField(max_length=100, unique=True, db_index=True)
    game_mode = models.CharField(max_length=50)
    game_type = models.CharField(max_length=50)
    queue_id = models.IntegerField(default=0)
    game_duration = models.IntegerField()
    game_creation = models.BigIntegerField(db_index=True)  # Add index for date filtering
    platform_id = models.CharField(max_length=10, default='NA1')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['game_creation']),
            models.Index(fields=['match_id']),
        ]

    def __str__(self):
        return f"Match {self.match_id} ({self.game_mode})"


class MatchParticipant(models.Model):
    """Represents a participant in a match"""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='participants')
    puuid = models.CharField(max_length=100)
    summoner_name = models.CharField(max_length=100)
    champion_id = models.IntegerField()
    champion_name = models.CharField(max_length=100)
    team_id = models.IntegerField()
    win = models.BooleanField()
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    gold_earned = models.IntegerField()
    total_damage_dealt = models.IntegerField()
    total_damage_taken = models.IntegerField()
    vision_score = models.IntegerField()
    cs = models.IntegerField(help_text="Creep score")
    role = models.CharField(max_length=20, blank=True, help_text="Player role (e.g., SOLO, DUO, NONE)")
    lane = models.CharField(max_length=20, blank=True, help_text="Player lane (e.g., TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY)")

    class Meta:
        unique_together = ['match', 'puuid']
        ordering = ['team_id', 'summoner_name']

    def __str__(self):
        return f"{self.summoner_name} in {self.match.match_id}"


class AnalysisTile(models.Model):
    """Represents an analysis tile that groups friends for win rate analysis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_tiles')
    name = models.CharField(max_length=100)
    friends = models.ManyToManyField(Friend, related_name='analysis_tiles')
    match_filter = models.CharField(max_length=20, choices=[
        ('inclusive', 'Inclusive - Include matches with these players plus others'),
        ('exclusive', 'Exclusive - Only include matches with these friends + random players (no other friends)')
    ], default='inclusive')
    date_from = models.DateField(null=True, blank=True, help_text="Start date for match filtering (YYYY-MM-DD)")
    date_to = models.DateField(null=True, blank=True, help_text="End date for match filtering (YYYY-MM-DD)")
    max_matches_per_tile = models.IntegerField(default=50, help_text="Maximum number of matches to show per tile")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def get_filtered_matches(self, limit: int = None):
        """Get matches filtered by tile criteria with optional date range and limit"""
        from django.db.models import Q
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get friend PUUIDs
        friend_puuids = list(self.friends.values_list('puuid', flat=True))
        logger.info(f"AnalysisTile.get_filtered_matches: Found {len(friend_puuids)} friend PUUIDs for tile '{self.name}'")
        
        if not friend_puuids:
            logger.warning(f"AnalysisTile.get_filtered_matches: No friends found for tile '{self.name}'")
            return Match.objects.none()
        
        # Base query - matches where at least one friend participated
        base_query = Match.objects.filter(
            participants__puuid__in=friend_puuids
        ).distinct()
        
        logger.info(f"AnalysisTile.get_filtered_matches: Base query found {base_query.count()} matches")
        
        # Apply date range filter if specified
        if self.date_from or self.date_to:
            logger.info(f"AnalysisTile.get_filtered_matches: Applying date filter - from: {self.date_from}, to: {self.date_to}")
            if self.date_from:
                start_timestamp = int(datetime.combine(self.date_from, datetime.min.time()).timestamp() * 1000)
                base_query = base_query.filter(game_creation__gte=start_timestamp)
                logger.info(f"AnalysisTile.get_filtered_matches: Applied start date filter: {start_timestamp}")
            
            if self.date_to:
                end_timestamp = int(datetime.combine(self.date_to, datetime.max.time()).timestamp() * 1000)
                base_query = base_query.filter(game_creation__lte=end_timestamp)
                logger.info(f"AnalysisTile.get_filtered_matches: Applied end date filter: {end_timestamp}")
        else:
            logger.info(f"AnalysisTile.get_filtered_matches: No date filter applied - returning most recent matches")
        
        # Apply match filter logic
        if self.match_filter == 'exclusive':
            logger.info(f"AnalysisTile.get_filtered_matches: Applying exclusive filter")
            # Only include matches where ONLY these friends played (no other friends)
            all_friend_puuids = list(Friend.objects.filter(user=self.user).values_list('puuid', flat=True))
            other_friend_puuids = [p for p in all_friend_puuids if p not in friend_puuids]
            
            if other_friend_puuids:
                # Exclude matches where other friends participated
                base_query = base_query.exclude(
                    participants__puuid__in=other_friend_puuids
                )
                logger.info(f"AnalysisTile.get_filtered_matches: Excluded {len(other_friend_puuids)} other friends")
        
        # Apply limit (use tile's max_matches_per_tile if no limit specified)
        if limit is None:
            limit = self.max_matches_per_tile
        
        final_query = base_query.order_by('-game_creation')[:limit]
        logger.info(f"AnalysisTile.get_filtered_matches: Final query returns {final_query.count()} matches (limit: {limit})")
        
        return final_query

    @property
    def total_matches(self):
        """Get total number of matches for this tile"""
        return self.get_filtered_matches().count()

    @property
    def wins(self):
        """Get number of wins for this tile"""
        matches = self.get_filtered_matches()
        return MatchParticipant.objects.filter(
            match__in=matches,
            puuid__in=list(self.friends.values_list('puuid', flat=True)),
            win=True
        ).count()

    @property
    def losses(self):
        """Get number of losses for this tile"""
        matches = self.get_filtered_matches()
        return MatchParticipant.objects.filter(
            match__in=matches,
            puuid__in=list(self.friends.values_list('puuid', flat=True)),
            win=False
        ).count()

    @property
    def win_rate(self):
        """Calculate win rate percentage"""
        total = self.wins + self.losses
        if total == 0:
            return 0.0
        return (self.wins / total) * 100


class UserProfile(models.Model):
    """Extended user profile with Riot account information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    riot_id = models.CharField(max_length=100, blank=True, help_text="Riot ID (e.g., 'SummonerName#TAG')")
    puuid = models.CharField(max_length=100, blank=True, help_text="Riot PUUID")
    summoner_name = models.CharField(max_length=100, blank=True)
    tag_line = models.CharField(max_length=10, blank=True)
    region = models.CharField(max_length=10, default='na1')
    last_match_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.summoner_name or 'No Riot ID'}" 