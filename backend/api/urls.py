from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Friends
    path('friends/', views.FriendListView.as_view(), name='friend-list'),
    path('friends/<int:pk>/', views.FriendDetailView.as_view(), name='friend-detail'),
    path('friends/add-by-riot-id/', views.add_friend_by_riot_id, name='add-friend-by-riot-id'),
    
    # Matches
    path('matches/', views.MatchListView.as_view(), name='match-list'),
    path('matches/refresh/<str:puuid>/', views.RefreshMatchesView.as_view(), name='refresh-matches'),
    
    # Analysis Tiles
    path('tiles/', views.AnalysisTileListView.as_view(), name='tile-list'),
    path('tiles/<int:pk>/', views.AnalysisTileDetailView.as_view(), name='tile-detail'),
    path('tiles/<int:pk>/matches/', views.TileMatchesView.as_view(), name='tile-matches'),
    
    # Debug/Test endpoints
    path('test-riot-api/', views.test_riot_api, name='test-riot-api'),
] 