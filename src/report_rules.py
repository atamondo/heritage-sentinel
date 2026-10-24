# report_rules.py — the knowledge base. Domain vocabulary lives here and only here.

MATERIALS = {"stone", "ceramic", "metal", "wood", "textile"}
DAMAGE = {"crack", "loose_base", "fading", "rot", "corrosion"}
SEVERITIES = {"none", "minor", "major"}

def rule(conclusion, *premises):
    return (frozenset(premises), conclusion)

CLAUSES = [
    # material classes
    rule("inorganic", "material_stone"),
    rule("inorganic", "material_ceramic"),
    rule("inorganic", "material_metal"),
    rule("organic", "material_wood"),
    rule("organic", "material_textile"),
    # any damage type counts as damage
    *[rule("has_damage", f"damage_{d}") for d in sorted(DAMAGE)],
    # derived concept
    rule("structural_risk", "damage_crack", "damage_loose_base"),
    # integrity constraints: a conclusion starting with "invalid:" is a violation
    rule("invalid:rot_on_inorganic", "damage_rot", "inorganic"),
    rule("invalid:corrosion_on_organic", "damage_corrosion", "organic"),
    rule("invalid:none_but_damaged", "severity_none", "has_damage"),
    rule("invalid:structural_risk_marked_minor", "structural_risk", "severity_minor"),
    
    # part E: own rules
    # material & damage that can't coexist: a textile has no base to come loose.
    # rule("invalid:loose_base_on_textile", "damage_loose_base", "material_textile"),
    
    # Severity that doesn't fit the pattern: rot plus a crack in wood means
    # moisture is getting into a split, fiber is failing, so "minor" is an understatement.
    # rule("fiber_failure", "material_wood", "damage_rot", "damage_crack"),
    #rule("invalid:fiber_failure_marked_minor", "fiber_failure", "severity_minor"),
]