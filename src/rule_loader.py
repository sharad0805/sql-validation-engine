import yaml
from dataclasses import dataclass,field
from typing import Any,Optional

@dataclass

class Rule:
    rule_id:str
    table: str
    column :str
    rule_type : str
    severity : str
    description :str
    params :Optional[dict[str,Any]] = field(default_factory=dict)

    def __repr__(self):
        return f"[{self.rule_id}] {self.rule_type} on {self.table} {self.column} ({self.severity})"
    
def load_rules(config_path: str="config/rules.yaml") -> list[Rule]:
    with open(config_path,'r') as f:
        data = yaml.safe_load(f)

    rules = []
    for r in data.get("rules",[]):
        rule=Rule(
            rule_id = r["rule_id"],
            table   = r["table"],
            column  = r["column"],
            rule_type = r["rule_type"],
            severity=r["severity"],
            description=r["description"],
            params = r.get("params",{}),
        )
        rules.append(rule)

    return rules

def get_rules_for_table(table_name:str,config_path:str="config/rules.yaml")->list[Rule]:
    all_rules = load_rules(config_path)
    return [r for r in all_rules if r.table==table_name]   
    
