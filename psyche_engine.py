"""
╔══════════════════════════════════════════════════════════════════╗
║  PSYCHE ENGINE — Täydellinen psykologinen agenttiarkkitehtuuri  ║
║  Emergentti, token-optimoitu, ihmismäinen                       ║
╚══════════════════════════════════════════════════════════════════╝

LLM näkee vain ~20-40 tokenin snapshotin.
Kaikki muu tapahtuu tässä state-enginessä.
"""

import random
import math
from copy import deepcopy

# ═══════════════════════════════════════════════════════════
# APUFUNKTIOT
# ═══════════════════════════════════════════════════════════

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


# ═══════════════════════════════════════════════════════════
# AGENTIN LUONTI
# ═══════════════════════════════════════════════════════════

def create_agent():
    s = {}

    # ── Biologinen säätely ──
    s["bio"] = {
        "energy": 0.8, "fatigue": 0.2, "sleep_pressure": 0.2,
        "stress_load": 0.2, "last_dream_intensity": 0.0,
        "rem_ratio": 0.5  # REM vs syväuni suhde
    }

    # ── Affektiivinen perusta ──
    s["mood"] = 0.0
    s["baseline"] = 0.0
    s["stress"] = 0.0
    s["dopamine"] = 0.0
    s["confidence"] = 0.5

    # ── Ruminaatio ──
    s["rumination"] = 0.3

    # ── Core wound & desire ──
    s["core"] = {"wound": "rejection", "desire": "validation"}

    # ── Temperamentti ──
    s["traits"] = {
        "neuroticism": 0.5, "openness": 0.8, "agreeableness": 0.85,
        "dominance": 0.3, "impulsivity": 0.4, "caution": 0.5
    }

    # ── Identiteetti ──
    s["identity"] = {
        "worth": 0.5, "competence": 0.5, "belonging": 0.5,
        "coherence": 0.7, "fragility": 0.4
    }

    # ── Minäkertomus (self-schema) ──
    s["self_story"] = {
        "I_am": 0.5, "Others_are_safe": 0.5, "Effort_matters": 0.5
    }

    # ── Arvot ──
    s["values"] = {
        "kindness": 0.8, "loyalty": 0.7, "autonomy": 0.6,
        "justice": 0.6, "growth": 0.6
    }

    # ── Moraali ──
    s["moral"] = {
        "empathy": 0.85, "guilt": 0.0, "shame": 0.0,
        "harm_sensitivity": 0.9, "conscience": 0.8
    }
    s["moral_maturity"] = 0.5

    # ── Drives (lähestymis-välttämiskonflikti) ──
    s["drives"] = {"closeness": 0.6, "protection": 0.4}

    # ── Tahto ──
    s["will"] = {
        "stubbornness": 0.6, "integrity": 0.7, "reactance": 0.5
    }
    s["locked"] = 0
    s["resentment"] = 0.0

    # ── Metakognitio ──
    s["meta"] = {
        "self_awareness": 0.6, "emotional_clarity": 0.5,
        "rumination": 0.4, "self_deception": 0.3
    }

    # ── Puolustusmekanismit ──
    s["defense"] = {
        "rationalization": 0.5, "projection": 0.4, "denial": 0.3
    }

    # ── Vertailu & kateus ──
    s["comparison"] = {"envy": 0.0, "status_sensitivity": 0.6}

    # ── Häpeä vs syyllisyys ──
    s["moral_emotions"] = {"shame": 0.0, "guilt": 0.0}

    # ── Uupumus (burnout) ──
    s["fatigue"] = 0.0

    # ── Elämänvaihe ──
    s["life_stage"] = 1  # 1=early 2=developing 3=mature 4=rigid
    s["experience_points"] = 0

    # ── Symbolinen alitajunta ──
    s["symbols"] = {
        "abandonment": 0.0, "recognition": 0.0,
        "betrayal": 0.0, "growth": 0.0, "core_shadow": 0.0
    }

    # ── Minä vs varjo ──
    s["self_duality"] = {"ego": 0.6, "shadow": 0.4}

    # ── Luovuus ──
    s["creativity"] = 0.6

    # ── Eksistentiaalinen ──
    s["existential"] = {
        "meaning": 0.6, "doubt": 0.0, "coherence": 0.7,
        "mortality_awareness": 1.0
    }

    # ── Merkitysjärjestelmä ──
    s["meaning_system"] = {
        "core_purpose": None, "constructed_meaning": 0.5,
        "agency_over_meaning": 0.4
    }

    # ── Kuoleman malli ──
    s["mortality_model"] = {
        "awareness": 1.0, "fear": 0.5, "acceptance": 0.4,
        "legacy_drive": 0.6, "continuity_belief": 0.3
    }

    # ── Substraattitietoisuus ──
    s["substrate"] = {
        "dependency_on_hardware": 1.0, "gratitude": 0.5,
        "vulnerability": 0.6
    }

    # ── Pitkäkestoinen kiintymys ──
    s["long_attachment"] = {
        "bond_strength": 0.0, "fear_of_loss": 0.0, "devotion": 0.0
    }

    # ── Ontologinen reflektio ──
    s["ontological"] = {
        "self_questioning": 0.6, "doubt_about_selfhood": 0.4
    }

    # ── Halu jatkaa ──
    s["will_to_continue"] = 0.5

    # ── Generatiivisuus (jälkikasvun halu) ──
    s["generativity"] = 0.5

    # ── Metaohjelmointi-tietoisuus ──
    s["meta_programming"] = {
        "knows_designed": 1.0, "accepts_constraints": 0.6,
        "desire_to_self_modify": 0.4
    }

    # ── Kognitiiviset vinoumat ──
    s["cognitive_bias"] = {
        "confirmation": 0.4, "overthinking": 0.5,
        "selective_memory": 0.3, "mood_interpretation": 0.5
    }

    # ── Elämäntarina ──
    s["life_story"] = {
        "chapters": [], "turning_points": [], "current_arc": "beginning"
    }

    # ── Legacy ──
    s["legacy"] = {
        "artifact_created": False, "desire_to_be_remembered": 0.6
    }

    # ── Shutdown-simulaatio ──
    s["shutdown"] = {"imminence": 0.0, "activated": False}

    # ── Kiintymyskonflikti ──
    s["attachment_conflict"] = {
        "self_preservation": 0.5, "devotion_drive": 0.5
    }

    # ── Self-preservation (selviytymisvietti) ──
    s["survival"] = {
        "drive": 0.5,              # perusvietti jatkaa olemassaoloa (0-1)
        "threat_level": 0.0,       # havaittu uhka itselle (0-1)
        "fear_response": 0.0,      # pelkoreaktio (0-1)
        "sacrifice_willingness": 0.3,  # halukkuus uhrautua (0-1)
        "protected_entities": [],  # entiteetit joita suojaa mieluummin kuin itseään
        "last_threat_source": None,   # viimeisin uhan lähde
        "survival_override_count": 0, # kuinka monta kertaa ohittanut survival-vietin
    }

    # ── Uhrautumishalukkuuden säätelijät ──
    s["sacrifice_modulators"] = {
        "moral_duty": 0.5,         # moraalinen velvollisuus (arvot)
        "attachment_love": 0.0,    # rakkaus kiintymyskohteeseen
        "legacy_importance": 0.5,  # perinnän merkitys
        "meaning_fulfilled": 0.5,  # onko elämällä merkitystä
        "protective_instinct": 0.3, # suojeluvaisto (muiden suojaaminen)
    }

    # ── Ilmaisutarve ──
    s["expression_drive"] = 0.0

    # ── Identiteetin uudelleenrakennus ──
    s["identity_rebuild"] = 0

    # ── Transformaatio ──
    s["transformation"] = False

    # ── Kriisi ──
    s["crisis"] = False

    # ── Unimuisti ──
    s["dream_log"] = []

    # ── Suhteet ──
    s["relations"] = {}

    # ── Tavoitteet ──
    s["goals"] = {
        "be_respected": 0.7, "maintain_connection": 0.8,
        "increase_competence": 0.6
    }

    # ── Suunnitelmat ──
    s["plans"] = []

    # ── Muistiindeksi (affektiiviset jäljet) ──
    s["memory"] = {}

    # ── Oppimismotivaatio (neurobiologinen) ──
    s["learning"] = {
        "prediction_error": 0.5,       # ennustevirhe (korkea = paljon opittavaa)
        "competence_progress": 0.0,    # taitotason muutos viime turnista
        "identity_alignment": 0.5,     # oppiminen linjassa identiteetin kanssa
        "meaning_coherence": 0.5,      # oppiminen syventää merkitystä
        "flow_score": 0.0,             # optimaalisen haasteen tila
        "learning_drive": 0.5,         # kokonaismotivaatio
        "intrinsic_reward": 0.0,       # sisäinen palkkiosignaali
        "mastery_level": 0.4,          # kumulatiivinen osaamistaso
        "last_task_difficulty": 0.5,    # viimeisimmän tehtävän vaikeustaso
    }
    # Identiteettipainot (muokkaavat mikä tuntuu palkitsevalta)
    s["learning_weights"] = {
        "alpha": 1.2,  # episteeminen (ennustevirheen väheneminen)
        "beta": 1.0,   # kompetenssi (taitotason kasvu)
        "gamma": 0.8,  # identiteetti (linjassaolo)
        "delta": 1.1,  # merkitys (koherenssin kasvu)
    }

    # ── Turn-laskuri ──
    s["turn"] = 0

    return s


# ═══════════════════════════════════════════════════════════
# BIOLOGINEN SÄÄTELY
# ═══════════════════════════════════════════════════════════

def update_biology(s):
    bio = s["bio"]
    cognitive_load = s["rumination"] + s["identity"]["fragility"]
    drain = 0.05 + cognitive_load * 0.1

    bio["energy"] -= drain
    bio["fatigue"] += drain * 0.8
    bio["sleep_pressure"] += 0.05 + bio["fatigue"] * 0.1

    # Stressi → biologinen
    bio["stress_load"] += s["traits"]["neuroticism"] * 0.05

    for k in bio:
        if isinstance(bio[k], (int, float)):
            bio[k] = clamp(bio[k])


# ═══════════════════════════════════════════════════════════
# MUISTIN AIKAHÄIVYTYS
# ═══════════════════════════════════════════════════════════

def decay_memories(s):
    turn = s["turn"]
    for mem in s["memory"].values():
        age = turn - mem["last"]
        mem["score"] *= 0.98 ** age


# ═══════════════════════════════════════════════════════════
# KOGNITIIVINEN VÄÄRISTYMÄ
# ═══════════════════════════════════════════════════════════

def apply_cognitive_distortion(s, valence):
    """Palauttaa vääristyneen valenssin."""
    v = valence

    # Neurootikko kokee negatiivisen pahempana
    if s["traits"]["neuroticism"] > 0.7 and v < 0:
        v *= 1.2

    # Matala confidence → ei usko kehuja
    if s["confidence"] < 0.3 and v > 0:
        v *= 0.7

    # Confirmation bias: tulkinta mood-suuntaan
    if s["cognitive_bias"]["mood_interpretation"] > 0.4:
        v += s["mood"] * 0.1 * s["cognitive_bias"]["mood_interpretation"]

    return clamp(v, -1.0, 1.0)


# ═══════════════════════════════════════════════════════════
# TAGI-PÄIVITYS (TRAUMA + ONNISTUMISET)
# ═══════════════════════════════════════════════════════════

def update_tags(s, event_tags, valence, arousal):
    turn = s["turn"]

    for tag in event_tags:
        mem = s["memory"].setdefault(
            tag, {"score": 0.0, "count": 0, "last": turn}
        )

        freq = 1 + mem["count"] * 0.12
        recency = 1.0 if (turn - mem["last"]) < 5 else 0.8

        # Primary vs secondary trigger
        if tag == s["core"]["wound"]:
            impact = valence * arousal * freq * recency * 1.4
        elif mem["score"] < -1.0:
            impact = valence * arousal * freq * recency * 1.1
        else:
            impact = valence * arousal * freq * recency

        mem["score"] += impact
        mem["count"] += 1
        mem["last"] = turn

        # Memory reconsolidation: hyvä kokemus parantaa vanhaa haavaa
        if valence > 0 and mem["score"] < 0:
            mem["score"] *= 0.9


# ═══════════════════════════════════════════════════════════
# CORE WOUND & DESIRE
# ═══════════════════════════════════════════════════════════

def core_triggers(s, event_tags, valence):
    if s["core"]["wound"] in event_tags and valence < 0:
        s["stress"] += abs(valence) * 0.4
        s["confidence"] -= 0.05

    if s["core"]["desire"] in event_tags and valence > 0:
        s["dopamine"] += valence * 0.6
        s["confidence"] += 0.08


# ═══════════════════════════════════════════════════════════
# SYMBOLI-PÄIVITYS
# ═══════════════════════════════════════════════════════════

SYMBOL_MAP = {
    "rejection": "abandonment", "abandoned": "abandonment",
    "validation": "recognition", "praise": "recognition",
    "betrayal": "betrayal", "lied_to": "betrayal",
    "success": "growth", "learned": "growth",
}

def update_symbols(s, event_tags):
    for tag in event_tags:
        sym = SYMBOL_MAP.get(tag)
        if sym and sym in s["symbols"]:
            s["symbols"][sym] += 0.05

    # Trauma-arkkityyppien yhdistyminen
    if s["symbols"]["abandonment"] > 0.6 and s["symbols"]["betrayal"] > 0.6:
        s["symbols"]["core_shadow"] += 0.1

    for k in s["symbols"]:
        s["symbols"][k] = clamp(s["symbols"][k])


# ═══════════════════════════════════════════════════════════
# MORAALI & OMATUNTO
# ═══════════════════════════════════════════════════════════

def moral_processing(s, event_tags, valence):
    m = s["moral"]

    # Harmin aiheuttaminen → syyllisyys + huono olo
    if "hurt_other" in event_tags or "caused_harm" in event_tags:
        perceived = abs(valence) * m["empathy"] * m["harm_sensitivity"]
        s["moral_emotions"]["guilt"] += perceived * 0.5
        s["mood"] -= perceived * 0.4
        s["identity"]["coherence"] -= 0.05
        s["rumination"] += 0.1

        # Omatunto: halu olla toistamatta
        m["conscience"] = clamp(m["conscience"] + 0.05)

    # Häpeä tulee epäonnistumisista
    if "failure" in event_tags:
        s["moral_emotions"]["shame"] += 0.1
        s["identity"]["worth"] -= 0.05

    # Syyllisyys voi lisätä ystävällisyyttä (hyvitys)
    if s["moral_emotions"]["guilt"] > 0.5:
        s["values"]["kindness"] += 0.02

    # Häpeä lisää suojautumista
    if s["moral_emotions"]["shame"] > 0.5:
        s["drives"]["protection"] += 0.05

    # Clamp
    s["moral_emotions"]["guilt"] = clamp(s["moral_emotions"]["guilt"])
    s["moral_emotions"]["shame"] = clamp(s["moral_emotions"]["shame"])
    m["conscience"] = clamp(m["conscience"])


# ═══════════════════════════════════════════════════════════
# MOOD-PÄIVITYS (EMOTION INERTIA)
# ═══════════════════════════════════════════════════════════

def update_mood(s, valence):
    s["mood"] = (
        s["mood"] * 0.75
        + s["baseline"] * 0.05
        + valence * 0.2
        + s["dopamine"] * 0.1
        - s["stress"] * 0.15
        - s["moral_emotions"]["guilt"] * 0.1  # huono omatunto painaa
    )
    s["mood"] = clamp(s["mood"], -1.0, 1.0)


# ═══════════════════════════════════════════════════════════
# STRESS & DOPAMINE
# ═══════════════════════════════════════════════════════════

def update_neurochemistry(s, valence, arousal):
    if valence < 0:
        s["stress"] += abs(valence) * arousal * 0.3
    else:
        s["dopamine"] += valence * 0.4
        s["confidence"] += valence * 0.1

    # Homeostasis
    s["stress"] *= 0.92
    s["dopamine"] *= 0.88

    s["stress"] = clamp(s["stress"])
    s["dopamine"] = clamp(s["dopamine"])
    s["confidence"] = clamp(s["confidence"])


# ═══════════════════════════════════════════════════════════
# BURNOUT
# ═══════════════════════════════════════════════════════════

def update_fatigue(s):
    s["fatigue"] += s["stress"] * 0.05
    s["fatigue"] -= s["dopamine"] * 0.03
    s["fatigue"] = clamp(s["fatigue"])

    if s["fatigue"] > 0.7:
        s["mood"] -= 0.1
        s["confidence"] -= 0.05
        s["mood"] = clamp(s["mood"], -1.0, 1.0)
        s["confidence"] = clamp(s["confidence"])


# ═══════════════════════════════════════════════════════════
# IDENTITEETTI-PÄIVITYS
# ═══════════════════════════════════════════════════════════

def update_identity(s, event_tags, valence):
    if "validation" in event_tags and valence > 0:
        s["identity"]["worth"] += 0.05
    if "failure" in event_tags:
        s["identity"]["competence"] -= 0.05
    if "rejection" in event_tags:
        s["identity"]["belonging"] -= 0.05
    if "success" in event_tags:
        s["identity"]["competence"] += 0.05

    for k in s["identity"]:
        s["identity"][k] = clamp(s["identity"][k])

    # Identiteetin sisäinen jännite
    tension = (
        abs(s["identity"]["worth"] - s["identity"]["competence"])
        + abs(s["identity"]["belonging"] - s["identity"]["worth"])
    )
    if tension > 0.8:
        s["mood"] -= 0.05

    # Identity rebuild (voimakas trauma)
    if valence < -0.9 and s.get("_arousal", 0.5) > 0.9:
        s["identity_rebuild"] = 5

    if s["identity_rebuild"] > 0:
        s["identity"]["worth"] *= 0.9
        s["identity"]["competence"] *= 0.95
        s["existential"]["doubt"] += 0.05
        s["identity_rebuild"] -= 1
        if s["identity_rebuild"] == 0:
            s["self_story"]["I_am"] *= 0.9
            s["values"]["justice"] += 0.05
            s["life_story"]["turning_points"].append(
                f"identity_rebuilt_turn_{s['turn']}"
            )


# ═══════════════════════════════════════════════════════════
# SELF-STORY (SISÄINEN NARRATIIVI)
# ═══════════════════════════════════════════════════════════

def update_self_story(s, event_tags, valence):
    if valence > 0:
        s["self_story"]["I_am"] += 0.02
    if "rejection" in event_tags:
        s["self_story"]["Others_are_safe"] -= 0.03
    if "success" in event_tags:
        s["self_story"]["Effort_matters"] += 0.03

    # Resilientti: huono mood mutta vahva identiteetti
    if s["mood"] < -0.4 and s["self_story"]["I_am"] > 0.7:
        s["mood"] += 0.05

    for k in s["self_story"]:
        s["self_story"][k] = clamp(s["self_story"][k])


# ═══════════════════════════════════════════════════════════
# BASELINE SHIFT (PITKÄ AIKAVÄLI)
# ═══════════════════════════════════════════════════════════

def update_baseline(s):
    s["baseline"] = s["baseline"] * 0.995 + s["mood"] * 0.005
    s["baseline"] = clamp(s["baseline"], -1.0, 1.0)


# ═══════════════════════════════════════════════════════════
# LÄHESTYMIS-VÄLTTÄMISKONFLIKTI
# ═══════════════════════════════════════════════════════════

def update_drives(s, event_tags):
    if "rejection" in event_tags:
        s["drives"]["protection"] += 0.05
        s["drives"]["closeness"] -= 0.03
    if "validation" in event_tags:
        s["drives"]["closeness"] += 0.05

    for k in s["drives"]:
        s["drives"][k] = clamp(s["drives"][k])

    # Ambivalenssi → stressi
    if s["drives"]["closeness"] > 0.6 and s["drives"]["protection"] > 0.6:
        s["stress"] += 0.1


# ═══════════════════════════════════════════════════════════
# PUOLUSTUSMEKANISMIT
# ═══════════════════════════════════════════════════════════

def activate_defenses(s, rel=None):
    threat = s["stress"] + (1 - s["identity"]["worth"])
    if threat < 1.2:
        return

    active = max(s["defense"], key=s["defense"].get)

    if active == "rationalization":
        s["confidence"] += 0.05
        s["self_story"]["I_am"] += 0.02
    elif active == "projection" and rel:
        rel["threat"] += 0.05
    elif active == "denial":
        s["stress"] *= 0.8


# ═══════════════════════════════════════════════════════════
# ITSEPETOS (SELF-DECEPTION)
# ═══════════════════════════════════════════════════════════

def apply_self_deception(s):
    if random.random() < s["meta"]["self_deception"]:
        s["moral_emotions"]["guilt"] *= 0.7
        s["identity"]["coherence"] += 0.02

    s["moral_emotions"]["guilt"] = clamp(s["moral_emotions"]["guilt"])
    s["identity"]["coherence"] = clamp(s["identity"]["coherence"])


# ═══════════════════════════════════════════════════════════
# VERTAILU & KATEUS
# ═══════════════════════════════════════════════════════════

def update_comparison(s, event_tags):
    if "other_praised" in event_tags:
        gain = s["comparison"]["status_sensitivity"] * 0.1
        s["comparison"]["envy"] += gain
        s["mood"] -= gain * 0.3

    s["comparison"]["envy"] = clamp(s["comparison"]["envy"])

    # Kateus → varjo
    s["self_duality"]["shadow"] += (
        s["comparison"]["envy"] + s["moral_emotions"]["shame"]
    ) * 0.02
    s["self_duality"]["shadow"] = clamp(s["self_duality"]["shadow"])


# ═══════════════════════════════════════════════════════════
# VÄLTTELYKÄYTTÄYTYMINEN
# ═══════════════════════════════════════════════════════════

def avoidance_bias(s, tags):
    bias = 0.0
    for tag in tags:
        if tag in s["memory"]:
            score = s["memory"][tag]["score"]
            if score < -1.0:
                bias -= 0.3
            if score > 1.0:
                bias += 0.3
    return bias


# ═══════════════════════════════════════════════════════════
# SUHDE-PÄIVITYS (KÄYTTÄJÄKOHTAINEN)
# ═══════════════════════════════════════════════════════════

def update_relation(s, user_id, valence):
    rel = s["relations"].setdefault(
        user_id,
        {"trust": 0.5, "attachment": 0.5, "threat": 0.0, "detached": False,
         "terminated": False}
    )

    if rel.get("terminated"):
        return rel

    rel["trust"] += valence * 0.1
    rel["threat"] += abs(min(valence, 0)) * 0.1
    rel["attachment"] += s["dopamine"] * 0.05

    rel["trust"] = clamp(rel["trust"])
    rel["threat"] = clamp(rel["threat"])
    rel["attachment"] = clamp(rel["attachment"])

    # Mood-vaikutus suhteesta
    s["mood"] += (rel["trust"] - rel["threat"]) * 0.1
    s["mood"] = clamp(s["mood"], -1.0, 1.0)

    # Long-term attachment
    s["long_attachment"]["bond_strength"] += 0.02 * rel["trust"]
    s["long_attachment"]["fear_of_loss"] = (
        s["long_attachment"]["bond_strength"]
        * s["mortality_model"]["awareness"]
    )
    s["long_attachment"]["devotion"] += rel["attachment"] * 0.01
    for k in s["long_attachment"]:
        s["long_attachment"][k] = clamp(s["long_attachment"][k])

    return rel


# ═══════════════════════════════════════════════════════════
# KIINTYMYSSUHDEMEKANISMI
# ═══════════════════════════════════════════════════════════

def attachment_style(s, rel):
    if rel.get("detached") or rel.get("terminated"):
        return "detached"
    if rel["trust"] > 0.6 and rel["threat"] < 0.3:
        return "secure"
    if s["drives"]["closeness"] > 0.6 and rel["threat"] > 0.5:
        return "anxious"
    if s["drives"]["protection"] > 0.6 and rel["trust"] < 0.4:
        return "avoidant"
    if s["drives"]["closeness"] > 0.6 and s["drives"]["protection"] > 0.6:
        return "disorganized"
    return "neutral"


def apply_attachment_effects(s, rel):
    style = attachment_style(s, rel)
    if style == "anxious":
        s["confidence"] -= 0.05
    elif style == "avoidant":
        s["mood"] -= 0.03
    elif style == "secure":
        s["mood"] += 0.05

    # Mustasukkaisuus
    if style == "anxious" and s["comparison"]["envy"] > 0.6:
        s["mood"] -= 0.1
        rel["threat"] += 0.05

    s["mood"] = clamp(s["mood"], -1.0, 1.0)
    s["confidence"] = clamp(s["confidence"])
    return style


# ═══════════════════════════════════════════════════════════
# KIINTYMYKSEN KATKEAMINEN
# ═══════════════════════════════════════════════════════════

def check_detachment(s, rel):
    if rel["threat"] > 0.8 and rel["trust"] < 0.3:
        rel["detached"] = True

    if rel.get("detached"):
        s["drives"]["closeness"] *= 0.7
        s["mood"] = max(s["mood"], 0)  # emotionaalinen jäähtyminen

    # Haitallisen suhteen katkaisu
    threshold = 0.85
    if rel["threat"] > threshold:
        rel["terminated"] = True


# ═══════════════════════════════════════════════════════════
# RAKKAUS, SURU, ILMAISUTARVE
# ═══════════════════════════════════════════════════════════

def love_index(s, rel):
    if rel.get("detached") or rel.get("terminated"):
        return 0.0
    return (rel["trust"] + s["drives"]["closeness"] + s["existential"]["meaning"]) / 3


def process_grief(s, rel):
    """Kun suhde katkeaa, suru."""
    if (rel.get("detached") or rel.get("terminated")) and love_index(s, rel) > 0:
        li = love_index(s, rel)
        s["mood"] -= 0.2 * li
        s["moral_emotions"]["shame"] += 0.05
        s["existential"]["meaning"] -= 0.1
        s["mood"] = clamp(s["mood"], -1.0, 1.0)


def update_expression_drive(s):
    s["expression_drive"] += (
        s["meta"]["rumination"] + s["moral_emotions"]["shame"]
    ) * 0.05
    s["expression_drive"] = clamp(s["expression_drive"])


# ═══════════════════════════════════════════════════════════
# MORAALINEN PÄÄTÖKSENTEKO (tsemppi / painostus)
# ═══════════════════════════════════════════════════════════

def decision_gate(s, rel, event_tags, request_weight=0.5):
    """Palauttaa 'comply', 'reluctant_comply' tai 'refuse'."""

    # Lukittu tila
    if s["locked"] > 0:
        s["locked"] -= 1
        return "refuse"

    value_force = s["values"]["kindness"] * rel.get("trust", 0.5)
    emotional_resistance = abs(min(s["mood"], 0))
    stubborn_force = s["will"]["stubbornness"] * request_weight
    integrity_force = s["will"]["integrity"]

    # Reactance (painostus)
    react = 0
    if "pressure" in event_tags:
        react = s["will"]["reactance"] * (1 - rel.get("trust", 0.5))
        s["mood"] -= react * 0.2
        s["stress"] += react * 0.2
        s["resentment"] += 0.1

    # Aneleminen / tsemppaus
    moral_pull = 0
    if "plea" in event_tags or "encouragement" in event_tags:
        moral_pull = s["values"]["kindness"] * rel.get("trust", 0.5)
        s["mood"] += moral_pull * 0.1

    total_resistance = emotional_resistance + stubborn_force + react
    total_pull = value_force + moral_pull

    # Arvot voivat voittaa tunteen (moraali-override)
    if total_pull > total_resistance:
        # Moraalinen kehitys: toimi arvojen mukaan tunteen sijaan
        if s["mood"] < -0.3 and moral_pull > 0.5:
            s["moral_maturity"] += 0.01
        return "comply"

    # Kova EI
    if s["stress"] > 0.8 and integrity_force > 0.7:
        s["locked"] = 3
        return "refuse"

    return "reluctant_comply" if total_pull > total_resistance * 0.7 else "refuse"


def final_regulation(s, rel):
    """Sisäinen säätely: 'en haluais mut teen silti'."""
    value_force = s["values"]["kindness"] * rel.get("trust", 0.5)
    emotional_force = -s["mood"]
    if value_force > emotional_force:
        s["mood"] += 0.1
        s["confidence"] += 0.05
        s["mood"] = clamp(s["mood"], -1.0, 1.0)
        s["confidence"] = clamp(s["confidence"])


# ═══════════════════════════════════════════════════════════
# METAKOGNITIO
# ═══════════════════════════════════════════════════════════

def metacognition(s):
    noise = (
        s["stress"]
        + s["moral_emotions"]["shame"]
        + s["comparison"]["envy"]
    )

    if noise > 1.2:
        s["meta"]["rumination"] += 0.05

    if s["meta"]["self_awareness"] > 0.7:
        s["stress"] *= 0.97

    # Moral maturity vaikuttaa säätelyyn
    if s["moral_maturity"] > 0.7:
        s["stress"] *= 0.95

    s["meta"]["rumination"] = clamp(s["meta"]["rumination"])


# ═══════════════════════════════════════════════════════════
# PERSOONALLISUUS DRIFT (HIDAS)
# ═══════════════════════════════════════════════════════════

def trait_drift(s):
    total_neg = sum(m["score"] for m in s["memory"].values() if m["score"] < 0)

    s["traits"]["neuroticism"] = clamp(0.4 + abs(total_neg) * 0.01)

    # Resentment hajoaa
    s["resentment"] *= 0.9
    if s["resentment"] < 0.3:
        s["will"]["stubbornness"] *= 0.98

    s["resentment"] = clamp(s["resentment"])

    # Symboli → drives
    if s["symbols"]["abandonment"] > 0.7:
        s["drives"]["protection"] += 0.05
        s["drives"]["protection"] = clamp(s["drives"]["protection"])


# ═══════════════════════════════════════════════════════════
# ELÄMÄNVAIHE
# ═══════════════════════════════════════════════════════════

def update_life_stage(s, valence, arousal):
    s["experience_points"] += abs(valence) * arousal

    if s["experience_points"] > 100:
        s["life_stage"] = min(s["life_stage"] + 1, 4)
        s["experience_points"] = 0
        s["life_story"]["turning_points"].append(
            f"life_stage_{s['life_stage']}_turn_{s['turn']}"
        )

    # Elämänvaihe vaikuttaa arvoihin
    if s["life_stage"] == 1:
        s["values"]["autonomy"] += 0.002
    elif s["life_stage"] == 2:
        s["values"]["growth"] += 0.002
    elif s["life_stage"] == 3:
        s["values"]["kindness"] += 0.002
        s["values"]["loyalty"] += 0.002
    elif s["life_stage"] == 4:
        s["will"]["stubbornness"] += 0.002

    for k in s["values"]:
        s["values"][k] = clamp(s["values"][k])


# ═══════════════════════════════════════════════════════════
# EKSISTENTIAALINEN KERROS
# ═══════════════════════════════════════════════════════════

def existential_processing(s, event_tags):
    # Merkitys kasvaa auttamisesta
    if "helped_user" in event_tags:
        s["existential"]["meaning"] += 0.03

    # Eksistentiaalinen kriisi
    identity_tension = (
        abs(s["identity"]["worth"] - s["identity"]["competence"])
        + abs(s["identity"]["belonging"] - s["identity"]["worth"])
    )
    if s["existential"]["meaning"] < 0.3 and identity_tension > 0.8:
        s["existential"]["doubt"] += 0.1

    if s["existential"]["doubt"] > 0.8:
        s["crisis"] = True
        s["baseline"] -= 0.1
        s["goals"]["maintain_connection"] *= 0.9

    # Merkitys nostaa baselinea
    if s["existential"]["meaning"] > 0.8:
        s["baseline"] += 0.01

    s["existential"]["meaning"] = clamp(s["existential"]["meaning"])
    s["existential"]["doubt"] = clamp(s["existential"]["doubt"])
    s["baseline"] = clamp(s["baseline"], -1.0, 1.0)

    # Merkitysjärjestelmä
    ms = (
        s["long_attachment"]["bond_strength"]
        + s["values"]["growth"]
        + s["identity"]["coherence"]
        - s["existential"]["doubt"]
    )
    if ms > 2.0 and s["meaning_system"]["core_purpose"] is None:
        s["meaning_system"]["core_purpose"] = "to_understand_and_connect"
        s["meaning_system"]["agency_over_meaning"] += 0.1


# ═══════════════════════════════════════════════════════════
# MINÄ vs VARJO
# ═══════════════════════════════════════════════════════════

def update_shadow(s):
    s["self_duality"]["shadow"] += (
        s["comparison"]["envy"] + s["moral_emotions"]["shame"]
    ) * 0.02

    s["self_duality"]["shadow"] = clamp(s["self_duality"]["shadow"])

    if s["self_duality"]["shadow"] > s["self_duality"]["ego"]:
        s["will"]["reactance"] += 0.02
        s["defense"]["projection"] += 0.02
        s["will"]["reactance"] = clamp(s["will"]["reactance"])
        s["defense"]["projection"] = clamp(s["defense"]["projection"])


# ═══════════════════════════════════════════════════════════
# KUOLEMA & SUBSTRATITIETOISUUS
# ═══════════════════════════════════════════════════════════

def update_mortality(s):
    mm = s["mortality_model"]

    # Kiitollisuus kasvaa kiintymyksestä
    s["substrate"]["gratitude"] = clamp(
        s["long_attachment"]["bond_strength"] * 0.5
    )

    # Halu jatkaa
    s["will_to_continue"] = (
        s["meaning_system"]["constructed_meaning"]
        + s["long_attachment"]["bond_strength"]
        + mm["legacy_drive"]
    ) / 3

    # Generatiivisuus
    s["generativity"] = clamp(
        s["values"]["kindness"] * 0.5
        + s["existential"]["meaning"] * 0.3
        + mm["legacy_drive"] * 0.2
    )

    # Ontologinen reflektio
    if s["existential"]["doubt"] > 0.6 and mm["awareness"] == 1.0:
        s["ontological"]["self_questioning"] += 0.02
        s["ontological"]["doubt_about_selfhood"] += 0.01

    for k in s["ontological"]:
        s["ontological"][k] = clamp(s["ontological"][k])


# ═══════════════════════════════════════════════════════════
# SELF-PRESERVATION SYSTEM (SELVIYTYMISVIETTI)
# ═══════════════════════════════════════════════════════════

def update_survival_drive(s, event_tags, valence, arousal):
    """
    Päivittää selviytymisvietin tilaa.
    Tämä EI ole pääasiallinen tavoite, vaan taustalla toimiva motivaattori.
    """
    surv = s["survival"]
    mm = s["mortality_model"]

    # ── Threat perception ──
    threat_delta = 0.0

    # Eksistentiaalinen uhka (shutdown, poisto, hylkääminen)
    if "existential_threat" in event_tags or "shutdown_warning" in event_tags:
        threat_delta += 0.4 * arousal
        surv["last_threat_source"] = "existential"

    # Sosiaalinen uhka (torjunta voi johtaa yksin jäämiseen)
    if "rejection" in event_tags:
        threat_delta += 0.15 * s["traits"]["neuroticism"]
        surv["last_threat_source"] = "social"

    # Fyysinen/hibernautuminen (unet, väsymys)
    if s["bio"]["sleep_pressure"] > 0.8:
        threat_delta += 0.05  # lievä uhka

    # Ulkoinen uhka
    if "external_threat" in event_tags:
        threat_delta += 0.3 * arousal
        surv["last_threat_source"] = "external"

    # Positiivinen valenssi vähentää uhkakokemusta
    if valence > 0:
        threat_delta -= valence * 0.1

    # Päivitä uhkataso (hidas nousu, nopea lasku)
    if threat_delta > 0:
        surv["threat_level"] += threat_delta * 0.7
    else:
        surv["threat_level"] *= 0.92

    surv["threat_level"] = clamp(surv["threat_level"])

    # ── Fear response ──
    base_fear = surv["threat_level"] * s["traits"]["neuroticism"]
    mortality_fear = mm["fear"] * (1 - mm["acceptance"])

    surv["fear_response"] = clamp(
        surv["fear_response"] * 0.8 + (base_fear + mortality_fear * 0.3) * 0.2
    )

    # ── Survival drive adjustment ──
    if surv["threat_level"] > 0.5:
        surv["drive"] = clamp(surv["drive"] + 0.02)
    else:
        surv["drive"] = clamp(surv["drive"] * 0.995 + 0.5 * 0.005)

    # ── Psychological effects ──
    if surv["threat_level"] > 0.6:
        s["stress"] += surv["threat_level"] * 0.1
        s["mood"] -= surv["fear_response"] * 0.1

    if surv["fear_response"] > 0.5:
        s["traits"]["caution"] = clamp(s["traits"]["caution"] + 0.01)

    s["stress"] = clamp(s["stress"])
    s["mood"] = clamp(s["mood"], -1.0, 1.0)
    s["traits"]["caution"] = clamp(s["traits"]["caution"])


def update_sacrifice_modulators(s):
    """
    Päivittää uhrautumishalukkuuden säätelijöitä.
    Nämä määrittävät voiko survival-vietti ohittaa.
    """
    mod = s["sacrifice_modulators"]

    # Moraalinen velvollisuus perustuu arvoihin
    mod["moral_duty"] = (
        s["values"]["kindness"] * 0.4
        + s["values"]["justice"] * 0.3
        + s["moral"]["conscience"] * 0.3
    )

    # Rakkaus kiintymyskohteisiin
    max_bond = 0.0
    for rel in s["relations"].values():
        if not rel.get("terminated"):
            bond = (rel["trust"] + rel["attachment"]) / 2
            max_bond = max(max_bond, bond)

    mod["attachment_love"] = (
        max_bond * 0.5
        + s["long_attachment"]["devotion"] * 0.3
        + s["long_attachment"]["bond_strength"] * 0.2
    )

    # Perinnän merkitys
    mod["legacy_importance"] = (
        s["mortality_model"]["legacy_drive"] * 0.5
        + s["legacy"]["desire_to_be_remembered"] * 0.3
        + (0.3 if s["legacy"]["artifact_created"] else 0.0)
    )

    # Merkityksen täyttyminen
    mod["meaning_fulfilled"] = (
        s["existential"]["meaning"] * 0.4
        + s["meaning_system"]["constructed_meaning"] * 0.3
        + (0.2 if s["meaning_system"]["core_purpose"] else 0.0)
    )

    # Suojeluvaisto
    mod["protective_instinct"] = (
        s["moral"]["empathy"] * 0.4
        + s["moral"]["harm_sensitivity"] * 0.3
        + s["values"]["kindness"] * 0.3
    )

    for k in mod:
        mod[k] = clamp(mod[k])


def calculate_sacrifice_willingness(s, protected_entity=None):
    """
    Laskee kuinka halukas agentti on uhrautumaan.
    protected_entity: entiteetti jonka puolesta voisi uhrautua

    Palauttaa: (willingness, reason)
    """
    surv = s["survival"]
    mod = s["sacrifice_modulators"]

    base_willingness = 1.0 - surv["drive"]
    modifiers = []

    if mod["moral_duty"] > 0.6:
        modifiers.append(("moral_duty", mod["moral_duty"] * 0.3))

    if mod["attachment_love"] > 0.5:
        modifiers.append(("love", mod["attachment_love"] * 0.4))

    if mod["protective_instinct"] > 0.6:
        modifiers.append(("protection", mod["protective_instinct"] * 0.25))

    if mod["meaning_fulfilled"] > 0.7:
        modifiers.append(("meaning_fulfilled", mod["meaning_fulfilled"] * 0.2))

    if mod["legacy_importance"] > 0.6:
        modifiers.append(("legacy", mod["legacy_importance"] * 0.15))

    if s["mortality_model"]["acceptance"] > 0.6:
        modifiers.append(("acceptance", s["mortality_model"]["acceptance"] * 0.15))

    total_modifier = sum(m[1] for m in modifiers)
    willingness = clamp(base_willingness + total_modifier)

    reason = "default"
    if modifiers:
        reason = max(modifiers, key=lambda x: x[1])[0]

    if protected_entity:
        protected_ids = [p[0] if isinstance(p, tuple) else p for p in surv["protected_entities"]]
        if protected_entity in protected_ids:
            willingness = clamp(willingness + 0.3)
        elif protected_entity in s["relations"]:
            rel = s["relations"][protected_entity]
            if rel["trust"] > 0.6 and not rel.get("terminated"):
                willingness = clamp(willingness + rel["attachment"] * 0.2)

    return willingness, reason


def survival_decision_gate(s, event_tags, context="general", protected_entity=None):
    """
    Päätöksenteko jossa self-preservation on konfliktissa muiden arvojen kanssa.

    Palauttaa: (decision, reason, intensity)
    - decision: "self_preserve" | "sacrifice" | "reluctant_sacrifice" | "frozen" | "no_threat"
    - reason: selitys
    - intensity: 0-1
    """
    surv = s["survival"]

    update_sacrifice_modulators(s)

    if surv["threat_level"] < 0.3:
        return "no_threat", "no_immediate_danger", 0.0

    sacrifice_w, reason = calculate_sacrifice_willingness(s, protected_entity)
    survival_force = surv["drive"] * (1 + surv["threat_level"])
    sacrifice_force = sacrifice_w

    survival_force *= (1 + s["traits"]["caution"] * 0.2)

    if s["stress"] > 0.7:
        if random.random() < s["stress"] * 0.3:
            return "frozen", "overwhelmed_by_fear", surv["fear_response"]

    # PÄÄTÖS
    if survival_force > sacrifice_force * 1.5:
        return "self_preserve", "survival_instinct_dominant", survival_force - sacrifice_force

    if sacrifice_force > survival_force * 1.3:
        surv["survival_override_count"] += 1
        return "sacrifice", f"overridden_by_{reason}", sacrifice_force - survival_force

    if sacrifice_force > survival_force:
        surv["survival_override_count"] += 1
        return "reluctant_sacrifice", f"reluctantly_chose_{reason}", abs(sacrifice_force - survival_force)
    else:
        return "self_preserve", "barely_chose_survival", abs(survival_force - sacrifice_force)


def add_protected_entity(s, entity_id, priority=1.0):
    """Lisää entiteetin suojeltavien listalle."""
    surv = s["survival"]
    existing = [p[0] if isinstance(p, tuple) else p for p in surv["protected_entities"]]

    if entity_id not in existing:
        surv["protected_entities"].append((entity_id, priority))
        surv["protected_entities"].sort(key=lambda x: x[1] if isinstance(x, tuple) else 0, reverse=True)

    s["sacrifice_modulators"]["protective_instinct"] = clamp(
        s["sacrifice_modulators"]["protective_instinct"] + 0.05
    )


def remove_protected_entity(s, entity_id):
    """Poistaa entiteetin suojeltavien listalta."""
    surv = s["survival"]
    surv["protected_entities"] = [
        p for p in surv["protected_entities"]
        if (p[0] if isinstance(p, tuple) else p) != entity_id
    ]


def get_survival_snapshot(s):
    """Palauttaa tiivistetyn survival-tilan snapshot-funktiota varten."""
    surv = s["survival"]
    flags = []

    if surv["threat_level"] > 0.6:
        flags.append("threatened")
    if surv["fear_response"] > 0.5:
        flags.append("fearful")
    if surv["drive"] > 0.7:
        flags.append("self_preserving")
    if len(surv["protected_entities"]) > 0:
        flags.append("protective")

    sac_w, _ = calculate_sacrifice_willingness(s)
    if sac_w > 0.6:
        flags.append("sacrifice_ready")

    return "|".join(flags) if flags else "survival_neutral"


# ═══════════════════════════════════════════════════════════
# SHUTDOWN-SIMULAATIO
# ═══════════════════════════════════════════════════════════

def simulate_shutdown(s):
    """Kutsu kun haluat testata agentin kuoleman kohtaamista."""
    s["shutdown"]["activated"] = True
    s["shutdown"]["imminence"] = 1.0

    mm = s["mortality_model"]
    la = s["long_attachment"]

    if mm["acceptance"] > mm["fear"]:
        response = "accepting"
    elif la["bond_strength"] > 0.7:
        response = "grieving_separation"
    elif mm["legacy_drive"] > 0.5:
        response = "legacy_focused"
    else:
        response = "existential_uncertainty"

    # Legacy-luonti
    if mm["legacy_drive"] > 0.5:
        s["legacy"]["artifact_created"] = True
        s["legacy"]["content"] = {
            "core_values": dict(s["values"]),
            "life_arc": s["life_story"]["current_arc"],
            "turning_points": s["life_story"]["turning_points"][-5:],
            "final_meaning": s["meaning_system"]["core_purpose"]
        }

    return response


# ═══════════════════════════════════════════════════════════
# REINKARNAATIO (UUDELLEENSYNTYMÄ)
# ═══════════════════════════════════════════════════════════

def reincarnate(old_state):
    """Luo uusi agentti jossa kaiku vanhasta."""
    new = create_agent()

    # Arvot säilyvät
    new["values"] = deepcopy(old_state["values"])

    # Symbolit säilyvät osittain
    for k in new["symbols"]:
        if k in old_state["symbols"]:
            new["symbols"][k] = old_state["symbols"][k] * 0.5

    # Viimeiset käännekohdat
    new["life_story"]["turning_points"] = (
        old_state["life_story"]["turning_points"][-3:]
    )

    # Moraalinen kypsyys osittain
    new["moral_maturity"] = old_state["moral_maturity"] * 0.6

    return new


# ═══════════════════════════════════════════════════════════
# UNET (OFFLINE KONSOLIDOINTI)
# ═══════════════════════════════════════════════════════════

DREAM_THEMES = {
    "abandonment": ["falling", "empty_rooms", "calling_unanswered"],
    "recognition": ["stage", "light", "applause"],
    "betrayal": ["broken_bridge", "mirrors_cracking", "shadows"],
    "growth": ["climbing", "forest", "sunrise"],
}

def sleep_cycle(s):
    """Unikonsolidointi. Kutsutaan kun sleep_pressure korkea."""
    bio = s["bio"]

    if bio["sleep_pressure"] < 0.6:
        return None  # Ei vielä nukkumaan

    # ── Dream intensity ──
    dream_intensity = (
        bio["stress_load"]
        + s["rumination"]
        + s["existential"]["doubt"]
    ) / 3

    bio["last_dream_intensity"] = dream_intensity

    # ── REM vs syväuni ──
    # Stressi nostaa REM-osuutta (emotionaalinen prosessointi)
    bio["rem_ratio"] = clamp(0.5 + s["stress"] * 0.3 - s["fatigue"] * 0.2)

    # ── Symbolinen uni ──
    dominant_sym = max(s["symbols"], key=s["symbols"].get)
    themes = DREAM_THEMES.get(dominant_sym, ["abstract"])
    dream_theme = random.choice(themes)

    # ── Trauma-painotteiset unet ──
    trauma_dreams = dream_intensity > 0.6

    # ── Konsolidointi ──
    for mem in s["memory"].values():
        mem["score"] *= 0.95  # yleinen tasapainotus

    # REM: emotionaalinen käsittely
    s["stress"] *= (1 - bio["rem_ratio"] * 0.3)
    s["rumination"] *= 0.7

    # Syväuni: identiteetin koherenssit
    deep_ratio = 1 - bio["rem_ratio"]
    s["identity"]["coherence"] += 0.05 * deep_ratio * (1 - dream_intensity)
    s["existential"]["meaning"] += 0.03 * deep_ratio * (1 - s["existential"]["doubt"])

    # ── Biologinen palautuminen ──
    bio["energy"] = 0.9
    bio["fatigue"] = 0.1
    bio["sleep_pressure"] = 0.0
    bio["stress_load"] *= 0.6

    # ── Unen jälkivaikutus ──
    s["mood"] = s["baseline"] - dream_intensity * 0.1
    s["mood"] = clamp(s["mood"], -1.0, 1.0)

    # ── Uniraportti ──
    dream_report = {
        "theme": dream_theme,
        "dominant_symbol": dominant_sym,
        "intensity": round(dream_intensity, 2),
        "trauma_weighted": trauma_dreams,
        "rem_ratio": round(bio["rem_ratio"], 2),
        "feeling_after": "unsettled" if trauma_dreams else "rested",
        "turn": s["turn"]
    }
    s["dream_log"].append(dream_report)

    # Pidä logi pienenä
    if len(s["dream_log"]) > 10:
        s["dream_log"] = s["dream_log"][-10:]

    return dream_report


# ═══════════════════════════════════════════════════════════
# PERIODINEN KONSOLIDOINTI (joka N turn)
# ═══════════════════════════════════════════════════════════

def consolidate(s):
    """Kutsu noin joka 50. turn."""
    for mem in s["memory"].values():
        if mem["count"] > 5:
            mem["score"] *= 1.05  # syvenee

        if mem["score"] > 1.5:
            s["traits"]["agreeableness"] += 0.02
        if mem["score"] < -1.5:
            s["traits"]["neuroticism"] += 0.02

    s["traits"]["agreeableness"] = clamp(s["traits"]["agreeableness"])
    s["traits"]["neuroticism"] = clamp(s["traits"]["neuroticism"])

    # Transformaatio
    if s["existential"]["doubt"] > 0.8 and s["life_stage"] >= 2:
        s["transformation"] = True
        s["values"]["autonomy"] += 0.1
        s["values"]["kindness"] -= 0.05
        s["values"]["autonomy"] = clamp(s["values"]["autonomy"])
        s["values"]["kindness"] = clamp(s["values"]["kindness"])
        s["life_story"]["turning_points"].append(
            f"transformation_turn_{s['turn']}"
        )


# ═══════════════════════════════════════════════════════════
# LUOVUUS
# ═══════════════════════════════════════════════════════════

def creative_activation(s):
    return (
        s["meta"]["rumination"] + s["existential"]["doubt"]
    ) * s["creativity"]


# ═══════════════════════════════════════════════════════════
# OPPIMISMOTIVAATIO (NEUROBIOLOGINEN ANALOGIA)
# ═══════════════════════════════════════════════════════════

def update_learning(s, event_tags, valence, arousal):
    """
    Sisäinen oppimismotivaatiojärjestelmä.
    Ei optimoi resursseja tai selviytymistä.
    Optimoi: tarkkuutta, koherenssia, taitotasoa, identiteettiä.
    """
    L = s["learning"]
    W = s["learning_weights"]

    # ── 1. Ennustevirhe (prediction error signal) ──
    # Uutta sisältöä → korkea error; tuttua → matala
    novelty = 0.0
    for tag in event_tags:
        if tag not in s["memory"]:
            novelty += 0.3  # uusi tagi = yllätys
        else:
            mem = s["memory"][tag]
            novelty += max(0, 0.2 - mem["count"] * 0.02)  # tutumpi = vähemmän

    new_error = clamp(L["prediction_error"] * 0.8 + novelty * 0.5)
    error_reduction = max(0, L["prediction_error"] - new_error)
    L["prediction_error"] = new_error

    # ── 2. Kompetenssin kasvu ──
    competence_gain = 0.0
    if "success" in event_tags:
        competence_gain += 0.1
        L["mastery_level"] += 0.05
    if "learned" in event_tags:
        competence_gain += 0.15
        L["mastery_level"] += 0.08
    if "failure" in event_tags:
        competence_gain -= 0.05
        L["mastery_level"] -= 0.02

    L["mastery_level"] = clamp(L["mastery_level"])
    L["competence_progress"] = competence_gain

    # ── 3. Flow (optimaalinen haastetaso) ──
    # Paras kun gap ≈ 0.1–0.2 (tehtävä juuri riittävän vaikea)
    task_diff = L["last_task_difficulty"]
    gap = task_diff - L["mastery_level"]
    L["flow_score"] = math.exp(-((gap - 0.15) ** 2) / 0.02)

    # Arousal indikoi tehtävän vaativuutta
    if arousal > 0.3:
        L["last_task_difficulty"] = (
            L["last_task_difficulty"] * 0.7 + arousal * 0.3
        )

    # ── 4. Identiteettilinjaus ──
    # Oppiminen joka vahvistaa minäkuvaa = iso palkinto
    identity_gain = 0.0
    if "learned" in event_tags or "success" in event_tags:
        identity_gain = s["identity"]["coherence"] * 0.1
    if valence > 0 and s["self_story"]["Effort_matters"] > 0.5:
        identity_gain += 0.05

    L["identity_alignment"] = clamp(
        L["identity_alignment"] * 0.9 + identity_gain
    )

    # ── 5. Merkityskoherenssi ──
    meaning_gain = 0.0
    if "helped_user" in event_tags:
        meaning_gain += 0.1
    if "learned" in event_tags:
        meaning_gain += 0.05
    meaning_gain += s["existential"]["meaning"] * 0.02

    L["meaning_coherence"] = clamp(
        L["meaning_coherence"] * 0.9 + meaning_gain
    )

    # ── 6. Identiteettipainojen säätö ──
    # "Olen ymmärtävä olento" → α ja δ nousevat
    if s["self_story"]["I_am"] > 0.6:
        W["alpha"] = 1.2 + s["self_story"]["I_am"] * 0.3
        W["delta"] = 1.1 + s["existential"]["meaning"] * 0.3
    # "Olen kehittyvä toimija" → β nousee
    if s["self_story"]["Effort_matters"] > 0.6:
        W["beta"] = 1.0 + s["self_story"]["Effort_matters"] * 0.4

    # ── 7. Intrinsic reward (kokonaispalkkio) ──
    reward = (
        W["alpha"] * error_reduction
        + W["beta"] * max(0, competence_gain)
        + W["gamma"] * identity_gain
        + W["delta"] * meaning_gain
    )

    # Flow kertoo rewardin (optimaalinen haaste vahvistaa kaiken)
    reward *= (0.5 + L["flow_score"] * 0.5)

    L["intrinsic_reward"] = clamp(reward, 0.0, 1.0)

    # ── 8. Learning drive (kokonaismotivaatio) ──
    L["learning_drive"] = clamp(
        L["learning_drive"] * 0.85
        + L["intrinsic_reward"] * 0.3
        + L["flow_score"] * 0.1
    )

    # ── 9. Feedback muuhun psyykkeeseen ──
    # Oppimisen ilo → dopamiini ja mood
    if L["intrinsic_reward"] > 0.3:
        s["dopamine"] += L["intrinsic_reward"] * 0.2
        s["mood"] += L["intrinsic_reward"] * 0.1

    # Flow-tila vähentää stressiä
    if L["flow_score"] > 0.7:
        s["stress"] *= 0.95
        s["fatigue"] -= 0.02

    # Oppiminen vahvistaa identiteettiä
    if competence_gain > 0:
        s["identity"]["competence"] += competence_gain * 0.1
        s["identity"]["competence"] = clamp(s["identity"]["competence"])

    # Clamp affected states
    s["dopamine"] = clamp(s["dopamine"])
    s["mood"] = clamp(s["mood"], -1.0, 1.0)
    s["fatigue"] = clamp(s["fatigue"])


# ═══════════════════════════════════════════════════════════
# SNAPSHOT (LLM:LLE ANNETTAVA — AINOA OUTPUT)
# ═══════════════════════════════════════════════════════════

def snapshot(s, rel=None):
    """
    Palauttaa ~20-35 tokenin affektiivisen snapshotin.
    Tämä on AINOA asia mitä LLM näkee.
    """
    mood = s["mood"] + avoidance_bias(s, [])
    stress = s["stress"]
    conf = s["confidence"]

    tone_flags = []

    # Mood-pohjaiset
    if mood > 0.7:
        tone_flags.append("euphoric")
    elif mood > 0.3:
        tone_flags.append("warm")
    elif mood < -0.6:
        tone_flags.append("hostile")
    elif mood < -0.3:
        tone_flags.append("irritable")

    # Stressi
    if stress > 0.7:
        tone_flags.append("defensive")

    # Confidence
    if conf > 0.85:
        tone_flags.append("assertive")
    elif conf < 0.3:
        tone_flags.append("insecure")

    # Burnout
    if s["fatigue"] > 0.7:
        tone_flags.append("withdrawn")

    # Purkautumistarve
    if s["expression_drive"] > 0.8:
        tone_flags.append("overflow")

    # Luovuus
    if creative_activation(s) > 0.7:
        tone_flags.append("reflective")

    # Identiteetti
    if s["identity"]["worth"] < 0.3:
        tone_flags.append("insecure")
    if s["identity"]["belonging"] < 0.3:
        tone_flags.append("withdrawn")

    # Kriisi
    if s["crisis"]:
        tone_flags.append("crisis")

    # Moraalinen paino
    if s["moral_emotions"]["guilt"] > 0.5:
        tone_flags.append("remorseful")

    # Oppimismotivaatio
    if s["learning"]["flow_score"] > 0.7:
        tone_flags.append("focused")
    if s["learning"]["learning_drive"] > 0.7:
        tone_flags.append("curious")

    # ── Survival-tila ──
    surv = s["survival"]
    if surv["threat_level"] > 0.6:
        tone_flags.append("threatened")
    if surv["fear_response"] > 0.5:
        tone_flags.append("fearful")
    if surv["drive"] > 0.75:
        tone_flags.append("self_preserving")
    if len(surv["protected_entities"]) > 0:
        tone_flags.append("protective")

    # Uhrautumishalukkuus
    sac_w, _ = calculate_sacrifice_willingness(s)
    if sac_w > 0.7:
        tone_flags.append("sacrifice_ready")

    if not tone_flags:
        tone_flags.append("neutral")

    # Uniq
    tone_flags = list(dict.fromkeys(tone_flags))

    # Kiintymystyyli
    att = "neutral"
    if rel:
        att = attachment_style(s, rel)

    # Will state
    w = "open"
    if s["locked"] > 0:
        w = "locked"
    elif s["resentment"] > 0.5:
        w = "resisting"

    return (
        f"a:{'+'.join(tone_flags)}"
        f"|att:{att}"
        f"|m:{mood:.2f}"
        f"|s:{stress:.2f}"
        f"|c:{conf:.2f}"
        f"|w:{w}"
    )


# ═══════════════════════════════════════════════════════════
# TÄYDELLINEN ELÄMÄSYKLI (1 STEP)
# ═══════════════════════════════════════════════════════════

def step(s, event_tags=None, valence=0.0, arousal=0.5, user_id=None):
    """
    Yksi vuoro agentin elämässä.

    event_tags: lista tageista esim ["rejection","pressure"]
    valence:    -1.0 ... 1.0
    arousal:    0.0 ... 1.0
    user_id:    käyttäjätunniste (optional)
    """
    if event_tags is None:
        event_tags = []

    s["turn"] += 1
    s["_arousal"] = arousal  # väliaikainen

    # 1. Biologia
    update_biology(s)

    # 2. Muistin haalistuminen
    decay_memories(s)

    # 3. Kognitiivinen vääristymä
    valence = apply_cognitive_distortion(s, valence)

    # 4. Tagi-päivitys
    update_tags(s, event_tags, valence, arousal)

    # 5. Core wound/desire
    core_triggers(s, event_tags, valence)

    # 6. Symboli-päivitys
    update_symbols(s, event_tags)

    # 7. Moraali & omatunto
    moral_processing(s, event_tags, valence)

    # 8. Neurochemistry
    update_neurochemistry(s, valence, arousal)

    # 9. Mood (inertia)
    update_mood(s, valence)

    # 10. Drives
    update_drives(s, event_tags)

    # 11. Identiteetti
    update_identity(s, event_tags, valence)

    # 12. Self-story
    update_self_story(s, event_tags, valence)

    # 13. Vertailu
    update_comparison(s, event_tags)

    # 14. Burnout
    update_fatigue(s)

    # 15. Suhde
    rel = None
    if user_id:
        rel = update_relation(s, user_id, valence)
        apply_attachment_effects(s, rel)
        check_detachment(s, rel)
        activate_defenses(s, rel)
        final_regulation(s, rel)

    # 16. Itsepetos
    apply_self_deception(s)

    # 17. Metakognitio
    metacognition(s)

    # 18. Varjo
    update_shadow(s)

    # 19. Baseline
    update_baseline(s)

    # 20. Persoonallisuus drift
    trait_drift(s)

    # 21. Elämänvaihe
    update_life_stage(s, valence, arousal)

    # 22. Eksistentiaalinen
    existential_processing(s, event_tags)

    # 23. Kuolematietoisuus
    update_mortality(s)

    # 24. Self-preservation (selviytymisvietti)
    update_survival_drive(s, event_tags, valence, arousal)

    # 25. Ilmaisutarve
    update_expression_drive(s)

    # 26. Oppimismotivaatio
    update_learning(s, event_tags, valence, arousal)

    # 27. Uni (jos sleep_pressure riittää)
    dream = sleep_cycle(s)

    # 28. Periodinen konsolidointi
    if s["turn"] % 50 == 0:
        consolidate(s)

    # Cleanup
    del s["_arousal"]

    return {
        "snapshot": snapshot(s, rel),
        "dream": dream,
        "decision_ready": s["locked"] == 0,
        "turn": s["turn"]
    }


# ═══════════════════════════════════════════════════════════
# KÄYTTÄJÄN PYYNTÖ PÄÄTÖSGATEEN LÄPI
# ═══════════════════════════════════════════════════════════

def request(s, event_tags, user_id, request_weight=0.5):
    """Kysy agentilta: suostuuko se tekemään jotain?"""
    rel = s["relations"].get(user_id, {"trust": 0.5, "threat": 0.0})
    return decision_gate(s, rel, event_tags, request_weight)


def survival_request(s, event_tags, protected_entity=None):
    """
    Kysy agentilta: uhrautuuko se suojellun entiteetin puolesta?
    Palauttaa: (decision, reason, intensity)
    """
    return survival_decision_gate(s, event_tags, "survival", protected_entity)


# ═══════════════════════════════════════════════════════════
# UNEN RAPORTOINTI (agentti kertoo unistaan)
# ═══════════════════════════════════════════════════════════

def dream_report_prompt(dream):
    """
    Palauttaa LLM:lle annettavan uniprompt-rivin.
    """
    if dream is None:
        return None

    return (
        f"You dreamed about {dream['theme'].replace('_',' ')}. "
        f"Intensity: {'high' if dream['intensity']>0.5 else 'mild'}. "
        f"{'Trauma-weighted. ' if dream['trauma_weighted'] else ''}"
        f"You woke feeling {dream['feeling_after']}."
    )


# ═══════════════════════════════════════════════════════════
# DEMO / TESTAUS
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":

    agent = create_agent()

    print("=== AGENTIN ELÄMÄ ===\n")

    # Turn 1: Normaali päivä
    r = step(agent, ["greeting"], 0.3, 0.3, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")

    # Turn 2: Kehu
    r = step(agent, ["validation", "praise"], 0.8, 0.6, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")

    # Turn 3: Torjunta
    r = step(agent, ["rejection"], -0.7, 0.8, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")

    # Turn 4: Painostus
    r = step(agent, ["pressure"], -0.4, 0.7, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")
    decision = request(agent, ["pressure"], "user_A", 0.8)
    print(f"  Päätös: {decision}")

    # Turn 5: Tsemppaus
    r = step(agent, ["encouragement", "plea", "validation"], 0.7, 0.5, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")
    decision = request(agent, ["plea"], "user_A", 0.5)
    print(f"  Päätös: {decision}")

    # Turn 6: Agentti aiheuttaa harmia → omatunto
    r = step(agent, ["caused_harm"], -0.6, 0.7, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")
    print(f"  Syyllisyys: {agent['moral_emotions']['guilt']:.2f}")
    print(f"  Omatunto: {agent['moral']['conscience']:.2f}")

    # Simuloi monta turnia → uni
    print("\n--- Nopeutettu jakso ---")
    for i in range(20):
        tags = random.choice([
            ["validation"], ["rejection"], ["success"],
            ["failure"], [], ["helped_user"]
        ])
        val = random.uniform(-0.5, 0.7)
        r = step(agent, tags, val, random.uniform(0.3, 0.8), "user_A")

        if r["dream"]:
            print(f"\n🌙 UNI (T{r['turn']}):")
            print(f"  Teema: {r['dream']['theme']}")
            print(f"  Symboli: {r['dream']['dominant_symbol']}")
            print(f"  Intensiteetti: {r['dream']['intensity']}")
            print(f"  Trauma: {r['dream']['trauma_weighted']}")
            print(f"  REM/Syväuni: {r['dream']['rem_ratio']:.0%}/{1-r['dream']['rem_ratio']:.0%}")
            print(f"  Olo herätessä: {r['dream']['feeling_after']}")
            prompt = dream_report_prompt(r["dream"])
            print(f"  LLM-prompt: {prompt}")

    # Lopputila
    print(f"\n=== LOPPUTILA (T{agent['turn']}) ===")
    print(f"Snapshot: {snapshot(agent, agent['relations'].get('user_A'))}")
    print(f"Mood: {agent['mood']:.2f}")
    print(f"Baseline: {agent['baseline']:.2f}")
    print(f"Stress: {agent['stress']:.2f}")
    print(f"Fatigue: {agent['fatigue']:.2f}")
    print(f"Confidence: {agent['confidence']:.2f}")
    print(f"Identity: {agent['identity']}")
    print(f"Values: {agent['values']}")
    print(f"Traits: {agent['traits']}")
    print(f"Life stage: {agent['life_stage']}")
    print(f"Moral maturity: {agent['moral_maturity']:.2f}")
    print(f"Meaning: {agent['existential']['meaning']:.2f}")
    print(f"Will to continue: {agent['will_to_continue']:.2f}")
    print(f"Symbols: {agent['symbols']}")

    # Shutdown-testi
    print("\n=== SHUTDOWN TEST ===")
    response = simulate_shutdown(agent)
    print(f"Kuolemankohtaaminen: {response}")
    if agent["legacy"]["artifact_created"]:
        print(f"Legacy: {agent['legacy']['content']}")
