import os
import re
from typing import Optional, Dict, Any
from datetime import datetime
import json
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import requests
from xml.etree.ElementTree import ParseError

class YouTubeService:
    """Service for handling YouTube video operations"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        
        # Debug logging (avoid emoji for Windows terminals)
        print("YouTubeService initialized")
        print(f"API Key configured: {'Yes' if self.api_key else 'No (will use PyTube fallback)'}")
        
        # Check if yt-dlp is available as additional fallback
        try:
            import yt_dlp
            self.has_ytdlp = True
            print("yt-dlp available as additional fallback")
        except ImportError:
            self.has_ytdlp = False
            print("yt-dlp not available (install with: pip install yt-dlp)")
        
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(url))
            if match:
                video_id = match.group(1)
                print(f"Extracted video ID: {video_id}")
                return video_id
        print(f"Could not extract video ID from URL: {url}")
        return None
    
    def validate_youtube_url(self, url: str) -> bool:
        """Validate if the provided URL is a valid YouTube URL"""
        return self.extract_video_id(url) is not None
    
    def get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """Get video metadata from YouTube Data API or PyTube as fallback"""
        print(f"Getting metadata for video ID: {video_id}")
        
        # Try YouTube Data API first if API key is available
        if self.api_key and self.api_key.strip():
            print("Trying YouTube Data API...")
            try:
                result = self._get_metadata_from_api(video_id)
                print("Successfully got metadata from YouTube Data API")
                return result
            except Exception as e:
                print(f"YouTube Data API failed: {e}")
                print("Falling back to PyTube...")
        else:
            print("No API key found, using PyTube...")
        
        # Try PyTube as fallback
        try:
            result = self._get_metadata_from_pytube(video_id)
            print("Successfully got metadata from PyTube")
            return result
        except Exception as e:
            print(f"PyTube also failed: {e}")
            
            # Try yt-dlp as additional fallback if available
            if self.has_ytdlp:
                print("Trying yt-dlp as additional fallback...")
                try:
                    result = self._get_metadata_from_ytdlp(video_id)
                    print("Successfully got metadata from yt-dlp")
                    return result
                except Exception as ytdlp_error:
                    print(f"yt-dlp also failed: {ytdlp_error}")
            
            print("Using mock data as final fallback")
            return self._get_mock_metadata(video_id)
    
    def _get_metadata_from_api(self, video_id: str) -> Dict[str, Any]:
        """Get metadata using YouTube Data API"""
        url = f"{self.base_url}/videos"
        params = {
            'id': video_id,
            'key': self.api_key,
            'part': 'snippet,statistics,contentDetails'
        }
        
        print(f"Making API request to: {url}")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
        data = response.json()
        if not data.get('items'):
            raise ValueError(f"Video not found or private/deleted (ID: {video_id})")
        
        video = data['items'][0]
        snippet = video['snippet']
        statistics = video['statistics']
        content_details = video['contentDetails']
        
        # Parse duration
        duration = self._parse_duration(content_details['duration'])
        
        # Format view count
        view_count = int(statistics.get('viewCount', 0))
        views = self._format_view_count(view_count)
        
        # Format published date
        published_date = snippet['publishedAt'][:10]  # YYYY-MM-DD format
        
        return {
            'title': snippet['title'],
            'description': snippet['description'][:500] + '...' if len(snippet['description']) > 500 else snippet['description'],
            'thumbnail': snippet['thumbnails']['maxresdefault']['url'] if 'maxresdefault' in snippet['thumbnails'] else snippet['thumbnails']['high']['url'],
            'duration': duration,
            'views': views,
            'published_at': published_date,
            'channel_name': snippet['channelTitle'],
            'video_id': video_id
        }
    
    def _get_metadata_from_pytube(self, video_id: str) -> Dict[str, Any]:
        """Get metadata using PyTube as fallback"""
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Fetching from PyTube: {url}")
        
        try:
            yt = YouTube(url, use_oauth=False, allow_oauth_cache=False)
            
            # Try to access basic properties to trigger any errors early
            title = yt.title
            author = yt.author
            length = yt.length
            views = yt.views
            publish_date = yt.publish_date
            description = yt.description
            thumbnail = yt.thumbnail_url
            
            print(f"PyTube data: Title='{title}', Author='{author}', Length={length}s")
            
            # Format duration
            duration = self._seconds_to_duration(length)
            
            # Format view count
            formatted_views = self._format_view_count(views)
            
            # Format published date
            published_date = publish_date.strftime('%Y-%m-%d') if publish_date else datetime.now().strftime('%Y-%m-%d')
            
            return {
                'title': title,
                'description': description[:500] + '...' if description and len(description) > 500 else (description or 'No description available'),
                'thumbnail': thumbnail,
                'duration': duration,
                'views': formatted_views,
                'published_at': published_date,
                'channel_name': author,
                'video_id': video_id
            }
        
        except Exception as e:
            print(f"PyTube detailed error: {type(e).__name__}: {str(e)}")
            raise e
    
    def _get_metadata_from_ytdlp(self, video_id: str) -> Dict[str, Any]:
        """Get metadata using yt-dlp as additional fallback"""
        try:
            import yt_dlp
            
            url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"Fetching from yt-dlp: {url}")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                title = info.get('title', 'Unknown Title')
                description = info.get('description', 'No description available')
                uploader = info.get('uploader', 'Unknown Channel')
                duration_seconds = info.get('duration', 0)
                view_count = info.get('view_count', 0)
                upload_date = info.get('upload_date', datetime.now().strftime('%Y%m%d'))
                thumbnail = info.get('thumbnail', f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg')
                
                print(f"yt-dlp data: Title='{title}', Uploader='{uploader}', Duration={duration_seconds}s")
                
                # Format duration
                duration = self._seconds_to_duration(duration_seconds)
                
                # Format view count
                formatted_views = self._format_view_count(view_count)
                
                # Format published date (yt-dlp returns YYYYMMDD format)
                try:
                    published_date = datetime.strptime(upload_date, '%Y%m%d').strftime('%Y-%m-%d')
                except:
                    published_date = datetime.now().strftime('%Y-%m-%d')
                
                return {
                    'title': title,
                    'description': description[:500] + '...' if len(description) > 500 else description,
                    'thumbnail': thumbnail,
                    'duration': duration,
                    'views': formatted_views,
                    'published_at': published_date,
                    'channel_name': uploader,
                    'video_id': video_id
                }
        
        except ImportError:
            raise Exception("yt-dlp not installed")
        except Exception as e:
            print(f"yt-dlp detailed error: {type(e).__name__}: {str(e)}")
            raise e
    
    def _get_mock_metadata(self, video_id: str) -> Dict[str, Any]:
        """Return mock metadata as final fallback"""
        print("Using mock metadata - both API and PyTube failed")
        return {
            'title': 'YouTube Video (Unable to fetch title)',
            'description': 'Unable to fetch video description at this time.',
            'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'duration': '10:30',
            'views': 'N/A',
            'published_at': datetime.now().strftime('%Y-%m-%d'),
            'channel_name': 'Unknown Channel',
            'video_id': video_id
        }
    
    def get_transcript(self, video_id: str) -> str:
        """Get video transcript using youtube-transcript-api"""
        print(f"Getting transcript for video ID: {video_id}")
        
        try:
            # Try to get transcript in different languages
            languages = ['en', 'en-US', 'en-GB']  # Try English variants first
            transcript_list = None
            
            # Find available transcripts to be more robust
            available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            
            for lang in languages:
                try:
                    transcript = available_transcripts.find_transcript([lang])
                    transcript_list = transcript.fetch()
                    print(f"Got transcript in language: {lang}")
                    break
                except NoTranscriptFound:
                    continue

            # If no specific language worked, try any available transcript
            if not transcript_list:
                for transcript in available_transcripts:
                    transcript_list = transcript.fetch()
                    print(f"Got auto-generated transcript in language: {transcript.language_code}")
                    break

            if not transcript_list:
                raise NoTranscriptFound("No suitable transcript found for this video.")

            # Combine all transcript segments
            full_transcript = ' '.join([item['text'] for item in transcript_list])
            
            # Clean up the transcript
            cleaned = self._clean_transcript(full_transcript)
            print(f"Transcript length: {len(cleaned)} characters")
            
            return cleaned
            
        except (NoTranscriptFound, TranscriptsDisabled) as e:
            print(f"Transcript not available for video {video_id}: {type(e).__name__}")
            print("Using sample transcript as fallback.")
            return self._get_sample_transcript()
        except ParseError as e:
            print(f"Transcript parsing failed for {video_id}. YouTube may have returned an invalid response. Error: {e}")
            print("Using sample transcript as fallback.")
            return self._get_sample_transcript()
        except Exception as e:
            print(f"An unexpected transcript error occurred for {video_id}: {type(e).__name__}: {e}")
            print("Using sample transcript as fallback.")
            return self._get_sample_transcript()
    
    def _clean_transcript(self, transcript: str) -> str:
        """Clean and format transcript text"""
        # Remove extra whitespace and normalize text
        cleaned = re.sub(r'\s+', ' ', transcript.strip())
        
        # Remove common filler words and phrases (optional)
        filler_patterns = [
            r'\b(um|uh|like|you know|so basically|okay|alright)\b',
            r'\[.*?\]',  # Remove bracketed content like [Music]
            r'\(.*?\)'   # Remove parenthetical content
        ]
        
        for pattern in filler_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _get_sample_transcript(self) -> None:
        """
        Returns None as a fallback. The blog generator will handle this.
        """
        return None
    
    def _parse_duration(self, duration_str: str) -> str:
        """Parse ISO 8601 duration (PT4M13S) to readable format (4:13)"""
        import re
        
        # Remove PT prefix
        duration_str = duration_str[2:]
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours
        if 'H' in duration_str:
            hours = int(re.search(r'(\d+)H', duration_str).group(1))
            duration_str = re.sub(r'\d+H', '', duration_str)
        
        # Extract minutes
        if 'M' in duration_str:
            minutes = int(re.search(r'(\d+)M', duration_str).group(1))
            duration_str = re.sub(r'\d+M', '', duration_str)
        
        # Extract seconds
        if 'S' in duration_str:
            seconds = int(re.search(r'(\d+)S', duration_str).group(1))
        
        # Format duration
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def _seconds_to_duration(self, total_seconds: int) -> str:
        """Convert seconds to readable duration format"""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def _format_view_count(self, view_count: int) -> str:
        """Format view count to readable string"""
        if view_count >= 1_000_000:
            return f"{view_count / 1_000_000:.1f}M"
        elif view_count >= 1_000:
            return f"{view_count / 1_000:.1f}K"
        else:
            return f"{view_count:,}" 