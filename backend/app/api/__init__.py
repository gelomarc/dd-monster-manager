from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

# Import routes after blueprint creation to avoid circular imports
from . import auth, campaigns, encounters, npcs, loot

# Register routes
api.add_url_rule('/auth/login', view_func=auth.login, methods=['POST'])
api.add_url_rule('/auth/register', view_func=auth.register, methods=['POST'])
api.add_url_rule('/auth/logout', view_func=auth.logout, methods=['POST'])

# Campaign routes
api.add_url_rule('/campaigns', view_func=campaigns.list_campaigns, methods=['GET'])
api.add_url_rule('/campaigns', view_func=campaigns.create_campaign, methods=['POST'])
api.add_url_rule('/campaigns/<int:id>', view_func=campaigns.get_campaign, methods=['GET'])
api.add_url_rule('/campaigns/<int:id>', view_func=campaigns.update_campaign, methods=['PUT'])
api.add_url_rule('/campaigns/<int:id>', view_func=campaigns.delete_campaign, methods=['DELETE'])

# Encounter routes
api.add_url_rule('/campaigns/<int:campaign_id>/encounters', view_func=encounters.list_encounters, methods=['GET'])
api.add_url_rule('/campaigns/<int:campaign_id>/encounters', view_func=encounters.create_encounter, methods=['POST'])
api.add_url_rule('/campaigns/<int:campaign_id>/encounters/<int:id>', view_func=encounters.get_encounter, methods=['GET'])
api.add_url_rule('/campaigns/<int:campaign_id>/encounters/<int:id>', view_func=encounters.update_encounter, methods=['PUT'])
api.add_url_rule('/campaigns/<int:campaign_id>/encounters/<int:id>', view_func=encounters.delete_encounter, methods=['DELETE'])

# NPC routes
api.add_url_rule('/campaigns/<int:campaign_id>/npcs', view_func=npcs.list_npcs, methods=['GET'])
api.add_url_rule('/campaigns/<int:campaign_id>/npcs', view_func=npcs.create_npc, methods=['POST'])
api.add_url_rule('/campaigns/<int:campaign_id>/npcs/<int:id>', view_func=npcs.get_npc, methods=['GET'])
api.add_url_rule('/campaigns/<int:campaign_id>/npcs/<int:id>', view_func=npcs.update_npc, methods=['PUT'])
api.add_url_rule('/campaigns/<int:campaign_id>/npcs/<int:id>', view_func=npcs.delete_npc, methods=['DELETE'])

# Loot routes
api.add_url_rule('/campaigns/<int:campaign_id>/encounters/<int:encounter_id>/loot', view_func=loot.list_loot, methods=['GET'])
api.add_url_rule('/campaigns/<int:campaign_id>/encounters/<int:encounter_id>/loot', view_func=loot.create_loot, methods=['POST'])
api.add_url_rule('/campaigns/<int:campaign_id>/encounters/<int:encounter_id>/loot/<int:id>', view_func=loot.get_loot, methods=['GET'])
api.add_url_rule('/campaigns/<int:campaign_id>/encounters/<int:encounter_id>/loot/<int:id>', view_func=loot.update_loot, methods=['PUT'])
api.add_url_rule('/campaigns/<int:campaign_id>/encounters/<int:encounter_id>/loot/<int:id>', view_func=loot.delete_loot, methods=['DELETE']) 