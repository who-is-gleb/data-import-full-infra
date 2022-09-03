import datetime
import pendulum
from typing import Optional, Dict


class GithubEvent:
    id: str
    created_at: str
    type: Optional[str]
    actor_id: Optional[int]
    repo_id: Optional[int]
    ref_type: Optional[str]
    push_id: Optional[int]
    commit_amount: int

    def __init__(self, event_dict: Dict):
        def get_possible_none_int(_dict: Dict, _key: str):
            return _dict.get(_key) if _dict.get(_key) is not None else 0

        def get_possible_none_str(_dict: Dict, _key: str):
            return _dict.get(_key) if _dict.get(_key) is not None else ''

        self.id = event_dict['id']
        self.created_at = pendulum.parse(event_dict['created_at']).int_timestamp
        self.type = get_possible_none_str(event_dict, 'type')
        self.actor_id = get_possible_none_int(event_dict.get('actor', {}), 'id')
        self.repo_id = get_possible_none_int(event_dict.get('repo', {}), 'id')
        self.ref_type = get_possible_none_str(event_dict.get('payload', {}), 'ref_type')
        self.push_id = get_possible_none_int(event_dict.get('payload', {}), 'push_id')
        self.commit_amount = len(event_dict.get('commits', []))

    @staticmethod
    def get_ch_table_schema() -> Dict:
        return {
            "id": "String",
            "created_at": "DateTime",
            "type": "String",
            "actor_id": "UInt64",
            "repo_id": "UInt64",
            "ref_type": "String",
            "push_id": "UInt64",
            "commit_amount": "UInt16"
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "type": self.type,
            "actor_id": self.actor_id,
            "repo_id": self.repo_id,
            "ref_type": self.ref_type,
            "push_id": self.push_id,
            "commit_amount": self.commit_amount,
        }
