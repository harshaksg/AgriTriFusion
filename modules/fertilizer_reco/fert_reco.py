# modules/fertilizer_reco/fert_reco.py
# Reads fertilizer_rules.csv and returns a recommendation dict.
import csv
import os

RULES_PATH = os.path.join('modules', 'fertilizer_reco', 'fertilizer_rules.csv')

def recommend_fertilizer(stage_json, rules_path=RULES_PATH):
    """
    stage_json: {'crop':'Tomato','stage':'Semi-Ripe','confidence':0.88}
    returns:
      {'fertilizer':'NPK', 'dose':'25 kg/acre', 'reason':'...', 'stage':'Semi-Ripe', 'crop':'Tomato'}
    """
    crop = stage_json.get('crop', 'Tomato')
    stage = stage_json.get('stage', 'Semi-Ripe')

    # Try to load CSV rules
    if os.path.exists(rules_path):
        try:
            with open(rules_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_crop = row.get('crop', '').strip()
                    row_stage = row.get('stage', '').strip()
                    if row_crop.lower() == crop.lower() and row_stage.lower() == stage.lower():
                        return {
                            'fertilizer': row.get('recommended_fertilizer', 'NPK'),
                            'dose': row.get('dose', '25 kg/acre'),
                            'reason': row.get('reason', 'Rule-based recommendation'),
                            'stage': stage,
                            'crop': crop
                        }
        except Exception:
            # if CSV read fails fall through to defaults
            pass

    # Fallback defaults
    if stage.lower() == 'unripe':
        return {'fertilizer':'Urea','dose':'40 kg/acre','reason':'Promotes vegetative growth','stage':stage,'crop':crop}
    if stage.lower() == 'semi-ripe' or 'semi' in stage.lower():
        return {'fertilizer':'NPK','dose':'25 kg/acre','reason':'Supports fruit formation','stage':stage,'crop':crop}
    return {'fertilizer':'MOP','dose':'20 kg/acre','reason':'Enhances color & firmness','stage':stage,'crop':crop}

if __name__ == "__main__":
    # quick smoke test
    print(recommend_fertilizer({'crop':'Tomato','stage':'Semi-Ripe'}))
