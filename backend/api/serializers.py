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
    win_rate = serializers.ReadOnlyField()
    wins = serializers.ReadOnlyField()
    losses = serializers.ReadOnlyField()
    total_matches = serializers.ReadOnlyField()
    
    class Meta:
        model = AnalysisTile
        fields = ['id', 'name', 'friends', 'match_filter', 'date_from', 'date_to', 'max_matches_per_tile', 'win_rate', 'wins', 'losses', 'total_matches', 'created_at']
        read_only_fields = ['id', 'created_at']


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