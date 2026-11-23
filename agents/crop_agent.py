from typing import Dict, Any, List

class CropAgent:
    """
    Agent 2: Crop Analysis Agent
    Responsibilities:
    - Analyses the selected crop, growth stage, and soil characteristics.
    - Evaluates water, nutrient, and physiological needs.
    - Highlights stage-specific crop vulnerabilities, pests, and optimal conditions.
    """
    def __init__(self):
        self.name = "Crop Analysis Agent"
        self.role = "Agronomic & Soil Compatibility Specialist"

        # Comprehensive knowledge base for common regional & staple crops
        self.crop_database = {
            "Rice": {
                "ideal_temp_min": 20, "ideal_temp_max": 35,
                "water_need": "High",
                "best_soils": ["Clay soil", "Clay Loam", "Loamy soil"],
                "stages": {
                    "Seedling / Germination": {
                        "focus": "Establishment & root system emergence",
                        "nutrient": "Light Nitrogen (N) starter, balanced Phosphorus (P) for rooting",
                        "water_rule": "Shallow water film (2-3 cm)",
                        "vulnerabilities": ["Damping off", "Thrips", "Crab damage"]
                    },
                    "Vegetative / Growing stage": {
                        "focus": "Tillering & leaf canopy development",
                        "nutrient": "Split application of Urea (Nitrogen) & Zinc sulfate",
                        "water_rule": "Maintain 3-5 cm standing water layer; avoid complete drying",
                        "vulnerabilities": ["Stem Borer (Yellow)", "Sheath Blight", "Blast", "Leaf folder"]
                    },
                    "Flowering / Panicle stage": {
                        "focus": "Panicle emergence and flowering pollination",
                        "nutrient": "Potassium (MOP) top dressing to reinforce grain strength",
                        "water_rule": "Critical moisture stage - never allow water stress",
                        "vulnerabilities": ["False Smut", "Brown Plant Hopper (BPH)", "Pollen wash-off from rain"]
                    },
                    "Harvesting / Maturity": {
                        "focus": "Grain hardening and golden ripening",
                        "nutrient": "No chemical fertilizer application",
                        "water_rule": "Drain field 10-14 days prior to harvest",
                        "vulnerabilities": ["Lodging (falling over in rain/wind)", "Grain shattering"]
                    }
                }
            },
            "Wheat": {
                "ideal_temp_min": 14, "ideal_temp_max": 25,
                "water_need": "Medium",
                "best_soils": ["Loamy soil", "Clay Loam", "Alluvial soil"],
                "stages": {
                    "Seedling / Germination": {
                        "focus": "Crown root initiation (CRI) at 21 days",
                        "nutrient": "Full dose of Phosphorus & Potassium basal + 1/3 Nitrogen",
                        "water_rule": "First critical irrigation at Crown Root Initiation",
                        "vulnerabilities": ["Termites", "Foot rot"]
                    },
                    "Vegetative / Growing stage": {
                        "focus": "Jointing and tillering expansion",
                        "nutrient": "First top dressing of Urea before second irrigation",
                        "water_rule": "Irrigate at jointing stage (40-45 days)",
                        "vulnerabilities": ["Yellow/Brown Rust", "Aphids", "Powdery Mildew"]
                    },
                    "Flowering / Panicle stage": {
                        "focus": "Heading and anthesis (flowering)",
                        "nutrient": "Foliar spray of Potassium Nitrate (13-0-45) if heat stress occurs",
                        "water_rule": "Irrigate at flowering, but avoid windy days to prevent lodging",
                        "vulnerabilities": ["Karnal Bunt", "Head Scab", "Terminal Heat Stress"]
                    },
                    "Harvesting / Maturity": {
                        "focus": "Dough to maturity hardening",
                        "nutrient": "Cease fertilization",
                        "water_rule": "Stop irrigation completely to allow uniform ripening",
                        "vulnerabilities": ["Pre-harvest sprouting if rains hit"]
                    }
                }
            },
            "Corn / Maize": {
                "ideal_temp_min": 18, "ideal_temp_max": 32,
                "water_need": "Medium to High",
                "best_soils": ["Loamy soil", "Sandy Loam", "Red soil"],
                "stages": {
                    "Seedling / Germination": {
                        "focus": "Coleoptile emergence and root anchoring",
                        "nutrient": "NPK 120:60:40 basal application with Zinc",
                        "water_rule": "Moist seedbed without stagnant puddles",
                        "vulnerabilities": ["Fall Armyworm (FAW) whorl feeding", "Seedling blight"]
                    },
                    "Vegetative / Growing stage": {
                        "focus": "Knee-high rapid stem elongation",
                        "nutrient": "Side-dressing with Urea at knee-high stage",
                        "water_rule": "Moderate irrigation; highly sensitive to waterlogging",
                        "vulnerabilities": ["Fall Armyworm", "Stem Borer", "Zinc deficiency (white bud)"]
                    },
                    "Flowering / Panicle stage": {
                        "focus": "Tasseling and silking (critical pollination)",
                        "nutrient": "Ensure adequate potassium for stalk stiffness",
                        "water_rule": "Most drought-sensitive period; drought reduces grain set",
                        "vulnerabilities": ["Silk drying from heat", "Tassel smut", "Ear rot"]
                    },
                    "Harvesting / Maturity": {
                        "focus": "Black layer formation at grain tip",
                        "nutrient": "None",
                        "water_rule": "Dry down field",
                        "vulnerabilities": ["Post-maturity ear rot", "Bird damage"]
                    }
                }
            },
            "Cotton": {
                "ideal_temp_min": 21, "ideal_temp_max": 35,
                "water_need": "Medium",
                "best_soils": ["Black soil (Regur)", "Clay Loam", "Deep Alluvial"],
                "stages": {
                    "Seedling / Germination": {
                        "focus": "Taproot penetration and cotyledon opening",
                        "nutrient": "Basal Phosphorus and Sulphur",
                        "water_rule": "Light irrigation; susceptible to crusting in heavy soils",
                        "vulnerabilities": ["Thrips", "Aphids", "Damping-off"]
                    },
                    "Vegetative / Growing stage": {
                        "focus": "Square (flower bud) formation and monopodial branching",
                        "nutrient": "Split Nitrogen application + Micronutrient mixture (Boron & Mg)",
                        "water_rule": "Alternate furrow irrigation to preserve oxygen",
                        "vulnerabilities": ["Pink Bollworm", "Whitefly", "Leaf Curl Virus (CLCuV)"]
                    },
                    "Flowering / Panicle stage": {
                        "focus": "Boll formation and rapid lint filling",
                        "nutrient": "Foliar spray of 1% Magnesium Sulphate + 1% Potassium Nitrate",
                        "water_rule": "Consistent moisture to prevent boll shedding",
                        "vulnerabilities": ["Boll rot in wet conditions", "Spotted Bollworm"]
                    },
                    "Harvesting / Maturity": {
                        "focus": "Boll bursting and lint drying",
                        "nutrient": "None",
                        "water_rule": "Discontinue irrigation 20 days prior to picking",
                        "vulnerabilities": ["Discoloration of lint from rain", "Trash content"]
                    }
                }
            },
            "Tomato": {
                "ideal_temp_min": 18, "ideal_temp_max": 30,
                "water_need": "Medium",
                "best_soils": ["Loamy soil", "Sandy Loam", "Red soil"],
                "stages": {
                    "Seedling / Germination": {
                        "focus": "Nursery hardening and transplant recovery",
                        "nutrient": "19-19-19 water soluble starter fertilizer",
                        "water_rule": "Keep soil moist but well-drained",
                        "vulnerabilities": ["Damping off", "Transplant shock"]
                    },
                    "Vegetative / Growing stage": {
                        "focus": "Canopy spread and staking setup",
                        "nutrient": "Balanced NPK + Calcium Nitrate to prevent blossom end rot",
                        "water_rule": "Regular drip cycles; avoid wetting foliage",
                        "vulnerabilities": ["Early Blight", "Tuta absoluta (Leaf miner)", "Whitefly"]
                    },
                    "Flowering / Panicle stage": {
                        "focus": "Flower cluster fruit set",
                        "nutrient": "Elevated Potassium and Boron for pollen viability",
                        "water_rule": "Uniform irrigation; fluctuations cause fruit splitting",
                        "vulnerabilities": ["Blossom End Rot (Calcium deficit)", "Late Blight in humidity"]
                    },
                    "Harvesting / Maturity": {
                        "focus": "Breaker to red ripe harvesting intervals",
                        "nutrient": "Calcium and Potassium maintenance",
                        "water_rule": "Reduce watering slightly to improve sugar brix and shelf life",
                        "vulnerabilities": ["Fruit borer", "Anthracnose rot"]
                    }
                }
            }
        }

        # Soil properties mapping
        self.soil_properties = {
            "Clay soil": {
                "water_retention": "Very High",
                "drainage": "Poor (High waterlogging risk)",
                "workability": "Heavy, prone to compaction when saturated",
                "nutrient_retention": "High CEC (cation exchange capacity)",
                "irrigation_adjustment": "Reduce irrigation frequency; allow top layer aeration."
            },
            "Loamy soil": {
                "water_retention": "Optimal / Balanced",
                "drainage": "Good",
                "workability": "Excellent, ideal crumb structure",
                "nutrient_retention": "Optimal",
                "irrigation_adjustment": "Standard scheduled irrigation with normal volume."
            },
            "Sandy soil": {
                "water_retention": "Low",
                "drainage": "Excessive (rapid leaching of nutrients)",
                "workability": "Easy, light",
                "nutrient_retention": "Low (prone to nitrogen/potassium leaching)",
                "irrigation_adjustment": "Frequent, light irrigation; split fertilizer applications."
            },
            "Black soil": {
                "water_retention": "High (Expands when wet, cracks when dry)",
                "drainage": "Slow",
                "workability": "Sticky when wet, hard when dry",
                "nutrient_retention": "Rich in Calcium, Potassium, Magnesium; low in Nitrogen",
                "irrigation_adjustment": "Avoid over-irrigation to prevent aeration loss and root asphyxiation."
            },
            "Red soil": {
                "water_retention": "Moderate",
                "drainage": "Free draining",
                "workability": "Porous and friable",
                "nutrient_retention": "Deficient in Nitrogen, Phosphorus, and Humus",
                "irrigation_adjustment": "Regular watering with organic matter incorporation."
            }
        }

    def analyze(self, crop: str, soil: str, stage: str) -> Dict[str, Any]:
        # Normalize crop name
        crop_match = None
        for key in self.crop_database.keys():
            if crop.lower() in key.lower() or key.lower() in crop.lower():
                crop_match = key
                break
        
        # Default fallback crop structure if unknown
        if not crop_match:
            crop_match = "Rice" # baseline reference

        crop_info = self.crop_database[crop_match]

        # Stage matching
        stage_match = None
        for s_key in crop_info["stages"].keys():
            if stage.lower() in s_key.lower() or s_key.lower() in stage.lower():
                stage_match = s_key
                break
        if not stage_match:
            stage_match = list(crop_info["stages"].keys())[1] # Default to vegetative

        stage_data = crop_info["stages"][stage_match]

        # Soil matching
        soil_match = None
        for s_key in self.soil_properties.keys():
            if soil.lower() in s_key.lower() or s_key.lower() in soil.lower():
                soil_match = s_key
                break
        if not soil_match:
            soil_match = "Clay soil"

        soil_data = self.soil_properties[soil_match]

        # Compatibility check
        soil_suitability = "Optimal" if any(soil_match.lower() in s.lower() for s in crop_info.get("best_soils", [])) else "Moderate"

        return {
            "agent": self.name,
            "role": self.role,
            "crop": crop,
            "matched_crop_profile": crop_match,
            "growth_stage": stage_match,
            "stage_focus": stage_data["focus"],
            "nutrient_needs": stage_data["nutrient"],
            "water_guideline": stage_data["water_rule"],
            "common_vulnerabilities": stage_data["vulnerabilities"],
            "soil_type": soil_match,
            "soil_properties": soil_data,
            "soil_suitability": soil_suitability,
            "optimal_temp_range": f"{crop_info['ideal_temp_min']}°C - {crop_info['ideal_temp_max']}°C",
            "summary": (
                f"Crop Profile: {crop} at {stage_match} in {soil_match}. "
                f"Soil compatibility is {soil_suitability}. Key focus: {stage_data['focus']}. "
                f"Target nutrient: {stage_data['nutrient']}."
            )
        }
