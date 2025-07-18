from django.contrib import admin
from .models import Friend, Match, MatchParticipant, AnalysisTile, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'summoner_name', 'tag_line', 'region', 'last_match_sync']
    list_filter = ['region', 'last_match_sync']
    search_fields = ['user__username', 'summoner_name', 'riot_id']


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ['summoner_name', 'tag_line', 'user', 'region', 'created_at']
    list_filter = ['region', 'created_at']
    search_fields = ['summoner_name', 'riot_id', 'user__username']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['match_id', 'game_mode', 'queue_id', 'game_duration', 'game_creation']
    list_filter = ['game_mode', 'queue_id', 'game_creation']
    search_fields = ['match_id']
    readonly_fields = ['created_at']


@admin.register(MatchParticipant)
class MatchParticipantAdmin(admin.ModelAdmin):
    list_display = ['summoner_name', 'match', 'champion_name', 'team_id', 'win', 'kills', 'deaths', 'assists']
    list_filter = ['team_id', 'win', 'champion_name']
    search_fields = ['summoner_name', 'match__match_id']


@admin.register(AnalysisTile)
class AnalysisTileAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'match_filter', 'win_rate', 'created_at']
    list_filter = ['match_filter', 'created_at']
    search_fields = ['name', 'user__username']
    filter_horizontal = ['friends']
    readonly_fields = ['win_rate', 'created_at', 'updated_at'] 