from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to ensure they are registered with SQLAlchemy
from .user import User
from .profiles import TenantProfile, OwnerProfile
from .listing import Listing, ListingImage
from .compatibility import CompatibilityScore
from .request import InterestRequest
from .chat import Chat, Message
from .notification import Notification
