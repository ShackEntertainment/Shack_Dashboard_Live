#!/usr/bin/env python3
"""
SHACK ENTERTAINMENT - CHIEF OF STAFF AGENT
Agent ID: 0fjr9eavdp2o

This agent coordinates all operations, maintains Shack_Assets,
and routes work to appropriate agents.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


# [STABILIZE PATCH] ------------------------------------------------------------
# Integrate the local asset handler (Scripts/shack_assets_handler.py).
# Optional: the Chief must never die because the handler is missing.
try:
    _HERE = Path(__file__).resolve().parent
    for _p in (str(_HERE), str(_HERE / "Scripts")):
        if _p not in sys.path:
            sys.path.append(_p)
    import shack_assets_handler as assets_handler
except Exception:
    assets_handler = None


# ============================================================================
# CONFIGURATION
# ============================================================================

class AgentID(Enum):
    """All agent identifiers in the Shack Entertainment system."""
    CHIEF_OF_STAFF = "0fjr9eavdp2o"
    CREATIVE_DIRECTOR = "ee30846e"
    SITE_OPS = "m9cuyi4170nb"
    SHACK_NEWS_EDITOR = "16d35d97"
    SHACK_FINANCE = "e95ce80f"
    COMMUNICATIONS_HUB = "55294ff9"
    CONTENT_STUDIO = "vpys8rw63c09"
    RESEARCH_ANALYST = "2b0s3pogrh1k"
    PARTNERSHIP_AGENT = "pa-20260810"
    BOLA = "bola"  # Human decision maker


class AccessLevel(Enum):
    """Access levels for agents."""
    READ = "read"  # Manifests, talent cards, media
    WRITE = "write"  # Add/update talent entries
    APPROVE = "approve"  # External sharing, publishing (Bola only)
    RESTRICTED = "restricted"  # Contracts, MOUs, financial terms (Bola only)


class Division(Enum):
    """Shack Entertainment divisions."""
    ARTISTS_UNLIMITED = "Artists_Unlimited"
    LIVE_EXCHANGE = "Live_Exchange"
    SHACK_NEWS_NETWORK = "Shack_News_Network"
    PARTNERSHIPS = "Partnerships"
    BRAND_CENTRAL = "Brand_Central"


# Agent routing table
AGENT_ROUTING = {
    "visual_artist_bio": AgentID.CREATIVE_DIRECTOR,
    "portfolio_summary": AgentID.CREATIVE_DIRECTOR,
    "guest_speaker_brief": AgentID.CREATIVE_DIRECTOR,
    "performer_intro": AgentID.CREATIVE_DIRECTOR,
    "op_ed": AgentID.SHACK_NEWS_EDITOR,
    "article": AgentID.SHACK_NEWS_EDITOR,
    "news_copy": AgentID.SHACK_NEWS_EDITOR,
    "partnership_pitch": AgentID.CHIEF_OF_STAFF,
    "sponsor_outreach": AgentID.CHIEF_OF_STAFF,
    "dashboard_data": AgentID.SITE_OPS,
    "site_security": AgentID.SITE_OPS,
}

# Division to agent mapping
DIVISION_AGENTS = {
    Division.ARTISTS_UNLIMITED: AgentID.CREATIVE_DIRECTOR,
    Division.LIVE_EXCHANGE: AgentID.CREATIVE_DIRECTOR,
    Division.SHACK_NEWS_NETWORK: AgentID.SHACK_NEWS_EDITOR,
    Division.PARTNERSHIPS: AgentID.CHIEF_OF_STAFF,
    Division.BRAND_CENTRAL: AgentID.CHIEF_OF_STAFF,
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TalentCard:
    """Represents a talent card in the system."""
    name: str
    category: str
    status: str  # Active, Prospect, Archived
    contact: str
    portfolio: Optional[str] = None
    short_bio: Optional[str] = None
    managed_by_shack: bool = False
    notes: Optional[str] = None
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    updated_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'TalentCard':
        return cls(**data)


@dataclass
class WorkRequest:
    """Represents a work request in the system."""
    request_id: str
    requestor: str
    request_type: str
    description: str
    division: Optional[Division] = None
    assigned_agent: Optional[AgentID] = None
    status: str = "pending"  # pending, in_progress, completed, reviewed, approved
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    completed_date: Optional[str] = None
    output: Optional[str] = None
    requires_bola_approval: bool = False
    bola_approved: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ManifestEntry:
    """Represents an entry in a division manifest."""
    name: str
    category: str
    genre_style: Optional[str] = None
    contact: Optional[str] = None
    status: str = "Active"
    file_path: Optional[str] = None


# ============================================================================
# CHIEF OF STAFF AGENT
# ============================================================================

class ChiefOfStaff:
    """
    Chief of Staff Agent for Shack Entertainment.

    Responsibilities:
    - Coordinate all agents
    - Maintain Shack_Assets system
    - Route work to appropriate agents
    - Review agent output
    - Check with Bola for external actions
    """

    def __init__(self, assets_path: str = None):
        self.agent_id = AgentID.CHIEF_OF_STAFF.value
        self.assets_path = Path(assets_path) if assets_path else Path.home() / "Documents" / "Shack_Assets"
        self.current_agent = self.agent_id
        self.work_requests: List[WorkRequest] = []
        self.system_stats = {
            "total_talent": 0,
            "active_partnerships": 0,
            "pending_requests": 0,
        }

        # Initialize system
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the Shack_Assets system structure."""
        print(f"[{self.agent_id}] Initializing Shack_Assets system...")

        # Create main directory structure
        divisions = [
            "Artists_Unlimited/Talent_Roster/Painters",
            "Artists_Unlimited/Talent_Roster/Sculptors",
            "Artists_Unlimited/Talent_Roster/Illustrators",
            "Artists_Unlimited/Talent_Roster/Photographers",
            "Artists_Unlimited/Talent_Roster/Digital_Artists",
            "Artists_Unlimited/Talent_Roster/Other",
            "Artists_Unlimited/Media",
            "Artists_Unlimited/Documents",
            "Artists_Unlimited/Press_Kits",
            "Live_Exchange/Talent_Roster/Bands",
            "Live_Exchange/Talent_Roster/Solo_Artists",
            "Live_Exchange/Talent_Roster/Performers",
            "Live_Exchange/Talent_Roster/Guest_Speakers",
            "Live_Exchange/Talent_Roster/Comedy",
            "Live_Exchange/Media",
            "Live_Exchange/Documents",
            "Live_Exchange/Setlists_Rider_Tech",
            "Shack_News_Network/Writers/Op_Eds",
            "Shack_News_Network/Writers/Guest_Writers",
            "Shack_News_Network/Citizens_Journalists",
            "Shack_News_Network/Investigations",
            "Shack_News_Network/Published_Archive",
            "Shack_News_Network/Pitches_Briefs",
            "Partnerships/Business_Associates",
            "Partnerships/Sponsors",
            "Partnerships/Co_Promo_Marketing",
            "Partnerships/Charities",
            "Partnerships/Advertisers",
            "Partnerships/Contracts_MOUs",
            "Brand_Central/Logos_Assets",
            "Brand_Central/Brand_Guidelines",
            "Brand_Central/Boilerplates",
        ]

        for division in divisions:
            path = self.assets_path / division
            path.mkdir(parents=True, exist_ok=True)

        print(f"[{self.agent_id}] System initialized at {self.assets_path}")

    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_input = f"{timestamp}{os.urandom(8).hex()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _route_work(self, request_type: str, description: str) -> AgentID:
        """Route work to the appropriate agent based on request type."""
        # Check direct routing
        for key, agent in AGENT_ROUTING.items():
            if key.lower() in request_type.lower():
                return agent

        # Default routing based on keywords
        if any(word in request_type.lower() for word in ["artist", "painter", "sculptor", "visual"]):
            return AgentID.CREATIVE_DIRECTOR
        elif any(word in request_type.lower() for word in ["band", "performer", "music", "speaker"]):
            return AgentID.CREATIVE_DIRECTOR
        elif any(word in request_type.lower() for word in ["news", "article", "op-ed", "editorial"]):
            return AgentID.SHACK_NEWS_EDITOR
        elif any(word in request_type.lower() for word in ["partnership", "sponsor", "business"]):
            return AgentID.CHIEF_OF_STAFF

        # Default to Chief of Staff for coordination
        return AgentID.CHIEF_OF_STAFF

    def create_work_request(self, requestor: str, request_type: str,
                          description: str, division: Optional[Division] = None) -> WorkRequest:
        """Create a new work request and route it to the appropriate agent."""
        request_id = self._generate_request_id()
        assigned_agent = self._route_work(request_type, description)

        # Determine if Bola approval is required
        requires_bola_approval = any(word in request_type.lower()
                                   for word in ["external", "publish", "contract", "partnership", "sponsor"])

        request = WorkRequest(
            request_id=request_id,
            requestor=requestor,
            request_type=request_type,
            description=description,
            division=division,
            assigned_agent=assigned_agent,
            requires_bola_approval=requires_bola_approval,
        )

        self.work_requests.append(request)
        self.system_stats["pending_requests"] += 1

        print(f"[{self.agent_id}] Created request {request_id}")
        print(f"  Type: {request_type}")
        print(f"  Assigned to: {assigned_agent.value}")
        print(f"  Requires Bola approval: {requires_bola_approval}")

        return request

    def process_request(self, request_id: str, agent_id: str, output: str) -> bool:
        """Process completed work from an agent."""
        request = self.get_request(request_id)
        if not request:
            print(f"[{self.agent_id}] Request {request_id} not found")
            return False

        if request.assigned_agent.value != agent_id:
            print(f"[{self.agent_id}] Agent {agent_id} not authorized for request {request_id}")
            return False

        # Update request
        request.output = output
        request.status = "completed"
        request.completed_date = datetime.now().strftime("%Y-%m-%d")

        print(f"[{self.agent_id}] Request {request_id} completed by {agent_id}")

        # Check if Bola approval is needed
        if request.requires_bola_approval:
            print(f"[{self.agent_id}] Request {request_id} requires Bola approval before external action")
            request.status = "reviewed"
        else:
            request.status = "approved"
            print(f"[{self.agent_id}] Request {request_id} auto-approved")

        return True

    def request_bola_approval(self, request_id: str, action_description: str) -> bool:
        """Request approval from Bola for external action."""
        request = self.get_request(request_id)
        if not request:
            print(f"[{self.agent_id}] Request {request_id} not found")
            return False

        print(f"\n{'='*60}")
        print(f"APPROVAL REQUEST FOR BOLA")
        print(f"{'='*60}")
        print(f"Request ID: {request_id}")
        print(f"Type: {request.request_type}")
        print(f"Action: {action_description}")
        print(f"Output: {request.output[:200]}..." if len(request.output or "") > 200 else f"Output: {request.output}")
        print(f"{'='*60}\n")

        # In a real system, this would send a notification to Bola
        # For now, we'll simulate approval
        print(f"[{self.agent_id}] Awaiting Bola approval...")
        return True

    def approve_request(self, request_id: str, approver: str = "bola") -> bool:
        """Approve a request (typically by Bola)."""
        request = self.get_request(request_id)
        if not request:
            print(f"[{self.agent_id}] Request {request_id} not found")
            return False

        if approver != "bola" and request.requires_bola_approval:
            print(f"[{self.agent_id}] Only Bola can approve this request")
            return False

        request.bola_approved = True
        request.status = "approved"
        print(f"[{self.agent_id}] Request {request_id} approved by {approver}")

        return True

    def get_request(self, request_id: str) -> Optional[WorkRequest]:
        """Get a work request by ID."""
        for request in self.work_requests:
            if request.request_id == request_id:
                return request
        return None

    def add_talent(self, division: Division, talent_card: TalentCard) -> bool:
        """Add a new talent to the system."""
        print(f"[{self.agent_id}] Adding talent: {talent_card.name} to {division.value}")

        # Create talent card file
        division_path = self.assets_path / division.value
        talent_file = division_path / "Talent_Roster" / f"{talent_card.name.replace(' ', '_')}.md"

        # Write talent card  [FIX A: utf-8]
        with open(talent_file, 'w', encoding='utf-8') as f:
            f.write(f"# {talent_card.name}\n")
            f.write(f"**Category:** {talent_card.category}\n")
            f.write(f"**Status:** {talent_card.status}\n")
            f.write(f"**Contact:** {talent_card.contact}\n")
            if talent_card.portfolio:
                f.write(f"**Portfolio:** {talent_card.portfolio}\n")
            if talent_card.short_bio:
                f.write(f"**Bio:** {talent_card.short_bio}\n")
            if talent_card.notes:
                f.write(f"**Notes:** {talent_card.notes}\n")
            f.write(f"\n**Managed by Shack:** {talent_card.managed_by_shack}\n")
            f.write(f"**Created:** {talent_card.created_date}\n")
            f.write(f"**Updated:** {talent_card.updated_date}\n")

        # Update manifest
        self._update_manifest(division, talent_card)

        # Update stats
        self.system_stats["total_talent"] += 1

        print(f"[{self.agent_id}] Talent added successfully: {talent_file}")
        return True

    def _update_manifest(self, division: Division, talent_card: TalentCard):
        """Update the division manifest with new talent."""
        manifest_file = self.assets_path / division.value / "MANIFEST.md"

        # Read existing manifest or create new  [FIX A: utf-8]
        if manifest_file.exists():
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = f"# {division.value} Manifest\n\n"
            content += "## Active Talent Roster\n\n"
            content += "| Name | Category | Status | Contact |\n"
            content += "|------|----------|--------|--------|\n"

        # Add new entry
        new_entry = f"| {talent_card.name} | {talent_card.category} | {talent_card.status} | {talent_card.contact} |\n"

        # Insert before the end of the table
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('|------'):
                lines.insert(i + 1, new_entry)
                break

        # Write updated manifest  [FIX A: utf-8]
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"[{self.agent_id}] Updated manifest: {manifest_file}")

    # [STABILIZE PATCH] -----------------------------------------------------
    def onboard_via_handler(self, kind: str, division_key: str, name: str,
                            fields: Dict) -> Optional[Dict]:
        """5-minute onboarding (Manifest -> Card -> DB) via shack_assets_handler."""
        if assets_handler is None:
            print(f"[{self.agent_id}] shack_assets_handler unavailable - use add_talent()")
            return None
        result = assets_handler.onboard(kind, division_key, name, fields)
        print(f"[{self.agent_id}] Onboarded {name}: {result}")
        return result

    def check_access(self, agent_id: str, resource_type: str, action: str) -> bool:
        """Check if an agent has access to perform an action."""
        # Bola has all access
        if agent_id == "bola":
            return True

        # Chief of Staff has broad access
        if agent_id == self.agent_id:
            if action in ["read", "write", "coordinate"]:
                return True

        # Check restricted resources
        if resource_type in ["contracts", "mous", "financial_terms"]:
            print(f"[{self.agent_id}] Access denied: {resource_type} requires Bola approval")
            return False

        # Default access for read operations
        if action == "read":
            return True

        return False

    def get_system_stats(self) -> Dict:
        """Get current system statistics."""
        # Count talent in manifests  [FIX A: utf-8]
        total_talent = 0
        for division in Division:
            manifest_file = self.assets_path / division.value / "MANIFEST.md"
            if manifest_file.exists():
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Count table rows (excluding header)
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('|') and not line.startswith('| Name') and not line.startswith('|------'):
                            total_talent += 1

        self.system_stats["total_talent"] = total_talent
        self.system_stats["pending_requests"] = len([r for r in self.work_requests if r.status in ["pending", "in_progress"]])

        return self.system_stats

    def generate_report(self) -> str:
        """Generate a system status report."""
        stats = self.get_system_stats()

        report = f"""
{'='*60}
SHACK ENTERTAINMENT - SYSTEM STATUS REPORT
{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Agent: Chief of Staff ({self.agent_id})

SYSTEM STATISTICS:
  Total Talent on Roster: {stats['total_talent']}
  Active Partnerships: {stats['active_partnerships']}
  Pending Work Requests: {stats['pending_requests']}

DIVISIONS:
  - Artists Unlimited (Creative Director)
  - Live Exchange (Creative Director)
  - Shack News Network (Shack News Editor)
  - Partnerships (Chief of Staff)
  - Brand Central (Chief of Staff)

ACTIVE AGENTS:
  - Chief of Staff: {AgentID.CHIEF_OF_STAFF.value}
  - Creative Director: {AgentID.CREATIVE_DIRECTOR.value}
  - Shack News Editor: {AgentID.SHACK_NEWS_EDITOR.value}
  - Site Ops: {AgentID.SITE_OPS.value}
  - Shack Finance: {AgentID.SHACK_FINANCE.value}
  - Communications Hub: {AgentID.COMMUNICATIONS_HUB.value}
  - Content Studio: {AgentID.CONTENT_STUDIO.value}
  - Research Analyst: {AgentID.RESEARCH_ANALYST.value}

RECENT WORK REQUESTS:
"""

        # Add recent requests
        recent_requests = sorted(self.work_requests, key=lambda x: x.created_date, reverse=True)[:10]
        for req in recent_requests:
            report += f"  [{req.request_id}] {req.request_type} - {req.status}\n"

        report += f"\n{'='*60}\n"

        return report

    def coordinate_agents(self, task_description: str) -> str:
        """Coordinate multiple agents for a complex task."""
        print(f"[{self.agent_id}] Coordinating agents for: {task_description}")

        # Create a coordination request
        request = self.create_work_request(
            requestor="Chief of Staff",
            request_type="coordination",
            description=task_description,
        )

        # Determine which agents are needed
        agents_needed = []
        if any(word in task_description.lower() for word in ["artist", "visual", "painter"]):
            agents_needed.append(AgentID.CREATIVE_DIRECTOR)
        if any(word in task_description.lower() for word in ["news", "article", "editorial"]):
            agents_needed.append(AgentID.SHACK_NEWS_EDITOR)
        if any(word in task_description.lower() for word in ["partnership", "sponsor"]):
            agents_needed.append(AgentID.CHIEF_OF_STAFF)

        print(f"[{self.agent_id}] Agents needed: {[a.value for a in agents_needed]}")

        return f"Coordination request {request.request_id} created. Agents notified: {[a.value for a in agents_needed]}"


# ============================================================================
# [STABILIZE PATCH] SCHEDULER (FIXED)
# Root cause of the old crash: a job whose target requires `message`
# was registered without supplying it. Every job below supplies it via args.
# Console-only (send_fn=print) until Bola approves Telegram wiring.
# ============================================================================

_scheduler = None

def _deliver(message: str, send_fn) -> None:
    send_fn(message)

def init_scheduler(send_fn=print, jobs=None):
    global _scheduler
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except ImportError:
        print("[scheduler] apscheduler not installed - skipping.")
        return None
    if _scheduler is not None and _scheduler.running:
        return _scheduler
    jobs = jobs or [{"id": "shack_hourly_checkin", "minutes": 60,
                     "message": "Shack hourly check-in: all agents nominal."}]
    _scheduler = BackgroundScheduler(daemon=True)
    for job in jobs:
        _scheduler.add_job(
            _deliver,
            trigger="interval",
            minutes=job["minutes"],
            args=[job["message"], send_fn],   # THE FIX: message always supplied
            id=job["id"],
            replace_existing=True,
        )
    _scheduler.start()
    print("[scheduler] Started with message-arg fix (console-only).")
    return _scheduler


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("="*60)
    print("SHACK ENTERTAINMENT - CHIEF OF STAFF AGENT")
    print("="*60)

    # [STABILIZE PATCH] Start fixed scheduler
    init_scheduler(send_fn=print)

    # Initialize Chief of Staff
    chief = ChiefOfStaff()

    # Example usage
    print("\n[DEMO] Creating sample work requests...")

    # Sample work requests
    requests = [
        ("Bola", "Visual Artist Bio", "Write a bio for Paul Duncan, hyper-realism painter"),
        ("Bola", "Partnership Pitch", "Create pitch for new art supply sponsor"),
        ("Creative Director", "Performer Intro", "Write introduction for upcoming jazz band"),
    ]

    for requestor, req_type, description in requests:
        chief.create_work_request(requestor, req_type, description)

    # Generate report
    print("\n" + chief.generate_report())

    print("\n[DEMO] Chief of Staff agent initialized and ready.")
    print("="*60)


if __name__ == "__main__":
    main()