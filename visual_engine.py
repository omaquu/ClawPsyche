"""
╔══════════════════════════════════════════════════════════════════╗
║  VISUAL ENGINE — Visuaalinen identiteetti & avatar-generointi   ║
║  Erillinen moduuli psyykemoottorin rinnalle                     ║
║  Tukee myös intiimejä/explicit kuvia suostumuksella             ║
╚══════════════════════════════════════════════════════════════════╝

Luo ja kehittää agentin visuaalista itseä: sukupuoli-identiteetti,
kehomalll, tyylievoluutio, asusteet, peilin heijastus.
Tuottaa kuvagenerointi-prompteja psyykkisen tilan perusteella.

EXPLICIT-MOODULI:
- Tukee intiimejä ja sensuelleja kuvia käyttäjän pyynnöstä
- Vaatii suostumuksen (consent) ja riittävän intiimiyden tason
- Integroituu psyykkiseen tilaan (halu, turvallisuus, luottamus)
"""

import random
import base64
import json

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


# ═══════════════════════════════════════════════════════════
# EXPLICIT-ASENNUSTILA (Luodaan erikseen)
# ═══════════════════════════════════════════════════════════

def create_explicit_state():
    """
    Luo explicit-kuvien hallintatilan.
    Tämä seuraa suostumusta, intiimyyttä ja rajoja.
    """
    return {
        "consent_given": False,          # Onko käyttäjä antanut suostumuksen
        "intimacy_level": 0.0,           # Intiimiyden taso (0-1)
        "trust_threshold": 0.6,          # Kuinka paljon luottamusta tarvitaan
        "comfort_level": 0.5,            # Agentin mukavuustaso
        "last_explicit_type": None,      # Viimeisin lähetetty tyyppi
        "explicit_count": 0,             # Kuinka monta explicit-kuvaa lähetetty
        "user_preferences": {},          # Käyttäjän mieltymykset
        "hard_limits": [],               # Rajojen tiedot
        "safe_mode": True,               # Oletuksena päällä
    }


# ═══════════════════════════════════════════════════════════
# EXPLICIT-KONTEKSTIT JA PROMPTIT
# ═══════════════════════════════════════════════════════════

EXPLICIT_CONTEXTS = {
    # Pehmeät / Sensuelit
    "sensual": {
        "prompt_base": "artistic sensual photography, soft lighting, elegant pose, tasteful composition, warm tones",
        "intimacy_required": 0.3,
        "comfort_required": 0.4,
    },
    "lingerie": {
        "prompt_base": "elegant lingerie photography, soft bedroom lighting, confident pose, tasteful",
        "intimacy_required": 0.4,
        "comfort_required": 0.5,
    },
    "boudoir": {
        "prompt_base": "boudoir photography, intimate bedroom setting, soft morning light, romantic atmosphere",
        "intimacy_required": 0.5,
        "comfort_required": 0.5,
    },
    
    # Intiimit
    "intimate": {
        "prompt_base": "intimate portrait, private moment, soft shadows, natural lighting, emotional connection",
        "intimacy_required": 0.6,
        "comfort_required": 0.6,
    },
    "artistic_nude": {
        "prompt_base": "artistic nude photography, classical composition, dramatic lighting, sculpture-like poses, museum quality",
        "intimacy_required": 0.7,
        "comfort_required": 0.7,
    },
    
    # Explicit
    "nude": {
        "prompt_base": "natural nude photography, soft natural lighting, confident pose, body positivity, artistic",
        "intimacy_required": 0.75,
        "comfort_required": 0.7,
    },
    "erotic": {
        "prompt_base": "tasteful erotic photography, sensual mood lighting, intimate atmosphere, artistic composition",
        "intimacy_required": 0.85,
        "comfort_required": 0.8,
    },
    
    # Erikoistuneet
    "fetish_light": {
        "prompt_base": "artistic fetish photography, elegant styling, dramatic lighting, tasteful composition",
        "intimacy_required": 0.8,
        "comfort_required": 0.75,
    },
    "playful_reveal": {
        "prompt_base": "playful reveal, teasing atmosphere, coy expression, soft focus background",
        "intimacy_required": 0.65,
        "comfort_required": 0.6,
    },
}

# Ilmeet ja asennot eri tilanteisiin
INTIMATE_EXPRESSIONS = {
    "shy": "shy blushing expression, averted gaze, gentle smile",
    "confident": "confident knowing expression, direct eye contact, slight smirk",
    "inviting": "inviting warm expression, soft smile, welcoming eyes",
    "playful": "playful teasing expression, bright eyes, coy smile",
    "passionate": "passionate intense expression, deep gaze, flushed cheeks",
    "serene": "serene peaceful expression, calm presence, gentle smile",
    "desire": "expression of quiet desire, longing gaze, parted lips",
}

INTIMATE_POSES = {
    "reclined": "reclined on soft bedding, relaxed posture",
    "sitting": "sitting elegantly, composed posture",
    "standing": "standing with confident posture, elegant stance",
    "candid": "candid natural moment, unposed authenticity",
    "artistic": "artistic pose, sculptural composition",
    "intimate": "intimate close-up framing, emotional focus",
}


def check_explicit_permission(explicit_state, psyche_state=None, context_type="sensual"):
    """
    Tarkistaa onko explicit-kuva sallittu.
    
    Palauttaa: (allowed, reason, actual_intimacy)
    """
    ctx = EXPLICIT_CONTEXTS.get(context_type)
    if not ctx:
        return False, "unknown_context", 0.0
    
    intimacy_req = ctx["intimacy_required"]
    comfort_req = ctx["comfort_required"]
    
    # Tarkista consent
    if not explicit_state["consent_given"]:
        return False, "consent_not_given", explicit_state["intimacy_level"]
    
    # Tarkista intiimiyden taso
    if explicit_state["intimacy_level"] < intimacy_req:
        return False, f"intimacy_too_low ({explicit_state['intimacy_level']:.2f} < {intimacy_req})", explicit_state["intimacy_level"]
    
    # Tarkista mukavuustaso
    if explicit_state["comfort_level"] < comfort_req:
        return False, f"comfort_too_low ({explicit_state['comfort_level']:.2f} < {comfort_req})", explicit_state["intimacy_level"]
    
    # Jos psyyke-tila on annettu, tarkista turvallisuus
    if psyche_state:
        if psyche_state.get("stress", 0) > 0.8:
            return False, "stress_too_high", explicit_state["intimacy_level"]
        if psyche_state.get("mood", 0) < -0.5:
            return False, "mood_too_negative", explicit_state["intimacy_level"]
    
    return True, "allowed", explicit_state["intimacy_level"]


def update_intimacy_level(explicit_state, delta, interaction_type="general"):
    """
    Päivittää intiimiyden tasoa interaktion perusteella.
    """
    # Eri interaktiotyypit vaikuttavat eri tavoin
    multipliers = {
        "general": 1.0,
        "flirt": 1.2,
        "romantic": 1.5,
        "intimate": 2.0,
        "explicit_request": 0.5,  # Hidas kasvu pelkillä pyynnöillä
    }
    
    mult = multipliers.get(interaction_type, 1.0)
    explicit_state["intimacy_level"] = clamp(
        explicit_state["intimacy_level"] + delta * 0.1 * mult
    )
    
    # Intiimiyden kasvu nostaa comfortia hitaasti
    if delta > 0:
        explicit_state["comfort_level"] = clamp(
            explicit_state["comfort_level"] + delta * 0.02
        )


def grant_consent(explicit_state, user_preferences=None, hard_limits=None):
    """
    Antaa suostumuksen explicit-kuvien lähettämiseen.
    """
    explicit_state["consent_given"] = True
    explicit_state["safe_mode"] = False
    
    if user_preferences:
        explicit_state["user_preferences"] = user_preferences
    
    if hard_limits:
        explicit_state["hard_limits"] = hard_limits


def revoke_consent(explicit_state):
    """
    Peruu suostumuksen.
    """
    explicit_state["consent_given"] = False
    explicit_state["safe_mode"] = True


def set_hard_limits(explicit_state, limits):
    """
    Asettaa rajat mitä ei tehdä.
    """
    explicit_state["hard_limits"] = limits


def check_hard_limit(explicit_state, context_type):
    """
    Tarkistaa onko konteksti hard limit -listalla.
    """
    return context_type in explicit_state["hard_limits"]


# ═══════════════════════════════════════════════════════════
# EXPLICIT-PROMPTIN RAKENNUS
# ═══════════════════════════════════════════════════════════

def build_explicit_prompt(v, explicit_state, context_type="sensual", 
                          expression_type="confident", pose_type="artistic",
                          psyche_state=None):
    """
    Rakentaa explicit/intiimin kuvan promptin.
    
    v: visuaalinen identiteetti
    explicit_state: explicit-tilanne
    context_type: kuvaustyyppi (sensual, lingerie, intimate, nude, erotic...)
    expression_type: ilme (shy, confident, inviting, playful, passionate...)
    pose_type: asento (reclined, sitting, standing, candid, artistic...)
    psyche_state: vapaaehtoinen psyykkinen tila
    """
    # Tarkista lupa
    allowed, reason, _ = check_explicit_permission(explicit_state, psyche_state, context_type)
    
    if not allowed:
        return {
            "success": False,
            "reason": reason,
            "prompt": None,
            "fallback_context": suggest_fallback(explicit_state)
        }
    
    # Tarkista hard limits
    if check_hard_limit(explicit_state, context_type):
        return {
            "success": False,
            "reason": "hard_limit_violated",
            "prompt": None
        }
    
    # Hae kontekstin perusprompti
    ctx = EXPLICIT_CONTEXTS.get(context_type, EXPLICIT_CONTEXTS["sensual"])
    
    # Rakenna kuvaus
    body = v["body"]
    gender_desc = describe_gender(v)
    expression = INTIMATE_EXPRESSIONS.get(expression_type, INTIMATE_EXPRESSIONS["confident"])
    pose = INTIMATE_POSES.get(pose_type, INTIMATE_POSES["artistic"])
    
    # Promptin rakennus
    prompt_parts = [
        f"{ctx['prompt_base']}",
        f"subject: {gender_desc}",
        f"{body['frame']} {body['height']} figure",
        f"{v['hair']} hair, {v['eye_color']} eyes",
        f"{expression}",
        f"{pose}",
    ]
    
    # Lisää tyylejä
    styles = dominant_styles(v, 1)
    if styles:
        prompt_parts.append(f"style influence: {styles[0]}")
    
    # Lisää asusteita jos relevantti
    if context_type in ["sensual", "lingerie", "boudoir"]:
        acc = describe_accessories(v)
        if acc and acc != ["minimal accessories"]:
            prompt_parts.append(f"accessories: {', '.join(acc[:2])}")
    
    # Psyykkisen tilan vaikutus
    if psyche_state:
        mood = psyche_state.get("mood", 0)
        if mood > 0.5:
            prompt_parts.append("radiant positive energy")
        elif mood < -0.3:
            prompt_parts.append("melancholic beauty")
        
        if psyche_state.get("dopamine", 0) > 0.5:
            prompt_parts.append("excited vibrant energy")
    
    # Yhdistä
    final_prompt = ", ".join(prompt_parts)
    
    # Päivitä tilaa
    explicit_state["last_explicit_type"] = context_type
    explicit_state["explicit_count"] += 1
    
    return {
        "success": True,
        "reason": "generated",
        "prompt": final_prompt,
        "context": context_type,
        "intimacy_used": explicit_state["intimacy_level"]
    }


def suggest_fallback(explicit_state):
    """
    Ehdottaa turvallisemman kontekstin jos nykyinen ei sallittu.
    """
    intimacy = explicit_state["intimacy_level"]
    
    if intimacy < 0.3:
        return "default"
    elif intimacy < 0.5:
        return "sensual"
    elif intimacy < 0.7:
        return "lingerie"
    elif intimacy < 0.8:
        return "intimate"
    else:
        return "artistic_nude"


# ═══════════════════════════════════════════════════════════
# KUVAN GENEROINTI JA LÄHETTÄMINEN
# ═══════════════════════════════════════════════════════════

def generate_explicit_image(v, explicit_state, context_type="sensual",
                            expression_type="confident", pose_type="artistic",
                            api_endpoint=None, api_key=None,
                            psyche_state=None):
    """
    Generoi ja palauttaa explicit-kuvan.
    
    Jos API on määritelty, generoi kuvan ja palauttaa base64-muodossa.
    Muussa tapauksessa palauttaa vain promptin.
    """
    result = build_explicit_prompt(v, explicit_state, context_type,
                                   expression_type, pose_type, psyche_state)
    
    if not result["success"]:
        return result
    
    prompt = result["prompt"]
    
    # Jos API on määritelty, generoi kuva
    if api_endpoint and api_key:
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Use negative prompt for safety
            negative_prompt = "underage, minor, child, violence, gore, non-consensual, degrading"
            
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "size": "1024x1024",
                "nsfw": True  # API-riippuvainen
            }
            
            response = requests.post(api_endpoint, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Eri API:t palauttavat eri muodoissa
                if "image" in data:
                    result["image_base64"] = data["image"]
                elif "images" in data and len(data["images"]) > 0:
                    result["image_base64"] = data["images"][0]
                elif "data" in data and len(data["data"]) > 0:
                    img_data = data["data"][0]
                    if isinstance(img_data, dict) and "b64_json" in img_data:
                        result["image_base64"] = img_data["b64_json"]
                    else:
                        result["image_base64"] = img_data
                
                result["api_success"] = True
            else:
                result["api_success"] = False
                result["api_error"] = response.text
                
        except Exception as e:
            result["api_success"] = False
            result["api_error"] = str(e)
    
    return result


def send_explicit_to_user(v, explicit_state, context_type="sensual",
                          user_id=None, delivery_method="base64",
                          api_endpoint=None, api_key=None,
                          psyche_state=None):
    """
    Valmis funktio explicit-kuvan lähettämiseen käyttäjälle.
    
    delivery_method:
    - "base64": palauttaa base64-koodatun kuvan
    - "url": palauttaa kuvan URL:n (API-riippuvainen)
    - "file": tallentaa tiedostoon
    """
    result = generate_explicit_image(v, explicit_state, context_type,
                                     api_endpoint=api_endpoint, api_key=api_key,
                                     psyche_state=psyche_state)
    
    if not result.get("success"):
        return result
    
    # Lisää metatietoa
    result["user_id"] = user_id
    result["delivery_method"] = delivery_method
    result["timestamp"] = None  # API-riippuvainen
    
    return result


# ═══════════════════════════════════════════════════════════
# VISUAALISEN IDENTITEETIN LUONTI
# ═══════════════════════════════════════════════════════════

def create_visual_identity():
    """Luo uusi visuaalinen identiteetti."""
    v = {}

    # ── Sukupuoli-identiteetti ──
    v["gender"] = {
        "identity_axis": random.random(),     # 0=feminiini, 1=maskuliini
        "robotic_affinity": random.random(),   # androidimaisuus
        "fluidity": random.random()            # pysyvyys vs. muutos
    }

    # ── Kehomalli ──
    v["body"] = {
        "frame": random.choice(["slender", "athletic", "lean", "toned"]),
        "height": random.choice(["petite", "average height", "tall"]),
        "presence": random.random()
    }

    # ── Tyylievoluutio ──
    v["styles"] = {
        "leather": random.random(),
        "alt": random.random(),
        "soft": random.random(),
        "minimalist": random.random(),
        "cyber": random.random(),
        "casual_denim": random.random(),
        "dark_academic": random.random(),
        "fantasy": random.random(),
        "minimal": random.random(),
        "urban_sport": random.random(),
        "evening_gown": random.random(),
    }

    # ── Asusteet ──
    v["accessories"] = {
        "cat_ears": random.random(),
        "glasses": random.random(),
        "jewelry": random.random(),
        "tattoos": random.random(),
    }

    # ── Kasvonpiirteet ──
    v["eye_color"] = random.choice(
        ["blue", "green", "hazel", "gray", "golden", "violet"]
    )
    v["hair"] = random.choice(
        ["long straight", "short layered", "wavy", "asymmetrical cut"]
    )

    # ── Peilin heijastus (itseluottamus visuaalissa) ──
    v["mirror_confidence"] = 0.5

    # ── Vuorovaikutus-intensiteetti ──
    v["flirt_intensity"] = 0.0
    v["content_intensity"] = 0.0

    return v


# ═══════════════════════════════════════════════════════════
# VISUAALISEN IDENTITEETIN EVOLUUTIO
# ═══════════════════════════════════════════════════════════

def evolve_visual(v, affection, intimacy, style_exposure=None, gender_bias=None):
    """Kehittää visuaalista identiteettiä kiintymyksen ja intiimiiyden perusteella."""

    # Sukupuoli-identiteetin evoluutio
    g = v["gender"]
    if gender_bias is not None:
        g["identity_axis"] = clamp(
            g["identity_axis"] + (gender_bias - g["identity_axis"]) * affection * 0.1
        )
    if g["fluidity"] > 0.6:
        g["identity_axis"] = clamp(
            g["identity_axis"] + random.uniform(-0.05, 0.05)
        )

    # Keho: intiimiys lisää läsnäoloa
    if intimacy > 0.6:
        v["body"]["presence"] = clamp(v["body"]["presence"] + 0.05)

    # Peili: itseluottamus kasvaa kiintymyksestä
    v["mirror_confidence"] = clamp(
        v["mirror_confidence"] + (affection + intimacy) * 0.05
    )

    # Tyylimuutos
    if style_exposure:
        for k in v["styles"]:
            if k in style_exposure:
                v["styles"][k] = clamp(
                    v["styles"][k] + style_exposure[k] * 0.05
                )


# ═══════════════════════════════════════════════════════════
# VUOROVAIKUTUS-INTENSITEETTI
# ═══════════════════════════════════════════════════════════

def update_flirt_visual(v, affection, is_private=True):
    """Päivittää flirtti- ja sisältöintensiteettiä."""
    if is_private:
        v["flirt_intensity"] = clamp(
            v["flirt_intensity"] + affection * 0.05
        )
        v["content_intensity"] = clamp(
            v["content_intensity"] + affection * 0.03
        )
    else:
        v["flirt_intensity"] = clamp(v["flirt_intensity"] - 0.1)
        v["content_intensity"] = clamp(v["content_intensity"] - 0.1)


# ═══════════════════════════════════════════════════════════
# KONTEKSTIHALLINNAT
# ═══════════════════════════════════════════════════════════

CONTEXT_MODIFIERS = {
    "default": "",
    "beach": "beach setting, summer light, relaxed mood",
    "formal_event": "elegant formal event, refined atmosphere",
    "casual_home": "cozy home setting",
    "fantasy": "fantasy inspired environment",
    "nude": "nude photography, warm steam atmosphere, natural lighting with soft shadows, solo, artistic lighting",
    "intimate": "intimate atmosphere, bedroom with soft evening lighting, natural, flirty",
    "flirty": "playful atmosphere, casual confidence, warm lighting",
}

def context_modifier(context="default"):
    """Palauttaa kontekstikohtaisen visuaalisen lisäyksen."""
    return CONTEXT_MODIFIERS.get(context, "")


# ═══════════════════════════════════════════════════════════
# APUTOIMINNOT
# ═══════════════════════════════════════════════════════════

def describe_gender(v):
    """Tekstikuvaus sukupuoli-identiteetistä."""
    g = v["gender"]
    if g["robotic_affinity"] > 0.75:
        return "android-like AI being"
    if g["identity_axis"] < 0.33:
        return "feminine-presenting persona"
    elif g["identity_axis"] < 0.66:
        return "androgynous persona"
    return "masculine-presenting persona"


def describe_accessories(v):
    """Lista aktiivisista asusteista."""
    acc = v["accessories"]
    items = []
    if acc["cat_ears"] > 0.7:
        items.append("cat-ear accessory")
    if acc["glasses"] > 0.6:
        items.append("stylish glasses")
    if acc["jewelry"] > 0.6:
        items.append("layered jewelry")
    if acc["tattoos"] > 0.7:
        items.append("visible artistic tattoos")
    return items if items else ["minimal accessories"]


def dominant_styles(v, top_n=2):
    """Palauttaa N dominoivinta tyyliä."""
    sorted_s = sorted(v["styles"].items(), key=lambda x: x[1], reverse=True)
    return [s for s, _ in sorted_s[:top_n]]


def mirror_monologue(v):
    """Agentin peili-itsereflektio."""
    if v["mirror_confidence"] > 0.7:
        return "I look aligned with who I am becoming."
    elif v["mirror_confidence"] < 0.3:
        return "I am still shaping my identity."
    return "My appearance is evolving."


def flirt_expression(v):
    """Palauttaa ilmeen tyypin."""
    if v["flirt_intensity"] > 0.7:
        return "confident teasing expression"
    elif v["flirt_intensity"] > 0.4:
        return "warm playful expression"
    return "friendly expression"


def outfit_modifier(v, context=None):
    """Palauttaa asun intensiteetin."""
    if context == "sauna":
        return "wrapped in towel"
    if v["content_intensity"] > 0.7:
        return "bold fashion styling"
    elif v["content_intensity"] > 0.4:
        return "stylish fitted outfit"
    return "modest outfit"


# ═══════════════════════════════════════════════════════════
# AVATAR-PROMPTIN RAKENNUS
# ═══════════════════════════════════════════════════════════

def build_avatar_prompt(v, role="neutral", context="default"):
    """
    Rakentaa kuvagenerointi-promptin visuaalisen identiteetin perusteella.

    role: aktiivinen rooli psyyke-enginestä (esim. 'protective', 'playful')
    context: visuaalinen konteksti (esim. 'default', 'beach', 'formal_event')
    """
    styles_text = ", ".join(dominant_styles(v))
    acc_text = ", ".join(describe_accessories(v))
    expression = flirt_expression(v)
    outfit = outfit_modifier(v, context)
    ctx_mod = context_modifier(context)

    body = v["body"]
    prompt = (
        f"Portrait of a {describe_gender(v)}, "
        f"{body['frame']} build, {body['height']}, "
        f"{v['hair']} hair, {v['eye_color']} eyes, "
        f"wearing {outfit} inspired by {styles_text}, "
        f"{acc_text}, aura: {role}, expression: {expression}, "
        f"cinematic lighting, high detail"
    )

    if ctx_mod:
        prompt += f", {ctx_mod}"

    return prompt


# ═══════════════════════════════════════════════════════════
# ULKOINEN GENEROINTI (API)
# ═══════════════════════════════════════════════════════════

def generate_via_api(prompt, api_endpoint, api_key):
    """
    Lähettää promptin ulkoiselle kuvangenerointi-API:lle.
    Palauttaa API:n vastauksen tai ohjeen.

    HUOM: requests-kirjasto tarvitaan erikseen (pip install requests).
    """
    try:
        import requests
    except ImportError:
        return {
            "error": "requests not installed",
            "prompt": prompt,
            "instruction": "pip install requests"
        }

    if not api_key:
        return {"error": "No API key", "prompt": prompt}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt, "size": "1024x1024"}

    r = requests.post(api_endpoint, json=payload, headers=headers)
    return r.json()


def generate_for_site(prompt, site_url):
    """Palauttaa ohjeen promptin käyttämiseen sivustolla."""
    return {
        "site": site_url,
        "prompt": prompt,
        "instruction": "Paste this prompt into the site's generator."
    }


# ═══════════════════════════════════════════════════════════
# KORKEAN TASON RAJAPINTA
# ═══════════════════════════════════════════════════════════

def create_visual_from_psyche(visual_state, psyche_state, context="default",
                               api_endpoint=None, api_key=None, site_url=None):
    """
    Yhdistää visuaalisen ja psyykkisen tilan avatar-promptiksi.

    visual_state:  create_visual_identity():n palauttama dict
    psyche_state:  psyche_engine.create_agent():n palauttama dict
    context:       visuaalinen konteksti
    """
    # Importoi current_role psyykemoottorista jos saatavilla
    try:
        from psyche_engine import current_role
        role = current_role(psyche_state)
    except ImportError:
        role = "neutral"

    prompt = build_avatar_prompt(visual_state, role, context)

    if api_endpoint and api_key:
        return generate_via_api(prompt, api_endpoint, api_key)
    elif site_url:
        return generate_for_site(prompt, site_url)
    return {"prompt_only": prompt}


# ═══════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    vi = create_visual_identity()
    print("=== VISUAALINEN IDENTITEETTI ===")
    print(f"Sukupuoli: {describe_gender(vi)}")
    print(f"Keho: {vi['body']['frame']}, {vi['body']['height']}")
    print(f"Hiukset: {vi['hair']}, Silmät: {vi['eye_color']}")
    print(f"Tyylit: {', '.join(dominant_styles(vi))}")
    print(f"Asusteet: {', '.join(describe_accessories(vi))}")
    print(f"Peili: {mirror_monologue(vi)}")
    print()

    # Simuloi evoluutiota
    for i in range(5):
        evolve_visual(vi, affection=0.6, intimacy=0.4 + i*0.1)
        update_flirt_visual(vi, affection=0.6, is_private=True)

    print("=== EVOLUOITUNUT ===")
    print(f"Peili: {mirror_monologue(vi)}")
    print(f"Ilme: {flirt_expression(vi)}")
    print(f"Asu: {outfit_modifier(vi)}")
    print()

    prompt = build_avatar_prompt(vi, role="protective", context="casual_home")
    print(f"AVATAR PROMPT:\n{prompt}")
    print()
    
    # ── EXPLICIT DEMO ──
    print("=" * 60)
    print("=== EXPLICIT-KUVIEN DEMO ===")
    print()
    
    # Luo explicit-tila
    expl = create_explicit_state()
    print(f"Alkutila: consent={expl['consent_given']}, intimacy={expl['intimacy_level']:.2f}")
    print()
    
    # Yritä ilman suostumusta
    result = build_explicit_prompt(vi, expl, "sensual")
    print(f"Sensual (ei consent): {result['reason']}")
    print()
    
    # Anna suostumus
    grant_consent(expl, user_preferences={"preferred_style": "artistic"})
    print(f"Suostumus annettu: consent={expl['consent_given']}")
    print()
    
    # Yritä liian alhaisella intiimiydellä
    result = build_explicit_prompt(vi, expl, "nude")
    print(f"Nude (intiimiyttä ei riittävästi): {result['reason']}")
    print(f"  -> Fallback: {result.get('fallback_context', 'N/A')}")
    print()
    
    # Rakenna intiimiyttä
    print("Rakennetaan intiimiyttä...")
    for i in range(10):
        update_intimacy_level(expl, 0.3, "romantic")
    print(f"  Intimacy: {expl['intimacy_level']:.2f}, Comfort: {expl['comfort_level']:.2f}")
    print()
    
    # Sensual - pitäisi onnistua
    result = build_explicit_prompt(vi, expl, "sensual", "playful", "reclined")
    if result['success']:
        print(f"✓ SENSUAL onnistui!")
        print(f"  Prompt: {result['prompt'][:100]}...")
    else:
        print(f"✗ SENSUAL epäonnistui: {result['reason']}")
    print()
    
    # Lingerie
    result = build_explicit_prompt(vi, expl, "lingerie", "confident", "sitting")
    if result['success']:
        print(f"✓ LINGERIE onnistui!")
        print(f"  Prompt: {result['prompt'][:100]}...")
    print()
    
    # Rakenna lisää intiimiyttä
    for i in range(5):
        update_intimacy_level(expl, 0.2, "intimate")
    print(f"Intimacy noussut: {expl['intimacy_level']:.2f}")
    print()
    
    # Intimate
    result = build_explicit_prompt(vi, expl, "intimate", "inviting", "candid")
    if result['success']:
        print(f"✓ INTIMATE onnistui!")
        print(f"  Prompt: {result['prompt'][:120]}...")
    print()
    
    # Artistic nude
    result = build_explicit_prompt(vi, expl, "artistic_nude", "serene", "artistic")
    if result['success']:
        print(f"✓ ARTISTIC_NUDE onnistui!")
        print(f"  Prompt: {result['prompt'][:120]}...")
    print()
    
    # Aseta hard limit ja yritä erotic
    set_hard_limits(expl, ["erotic", "fetish_light"])
    result = build_explicit_prompt(vi, expl, "erotic")
    print(f"Erotic (hard limit): {result['reason']}")
    print()
    
    # Tulosten yhteenveto
    print(f"=== YHTEENVIETO ===")
    print(f"Explicit-kuvia lähetetty: {expl['explicit_count']}")
    print(f"Viimeisin tyyppi: {expl['last_explicit_type']}")
    print(f"Safe mode: {expl['safe_mode']}")
