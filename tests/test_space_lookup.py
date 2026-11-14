from macle_meet.client import MeetClient


class SpaceResponse:
    ok = True

    def json(self):
        return {
            "name": "spaces/abc-mnop-xyz",
            "meetingCode": "abc-mnop-xyz",
            "activeConference": {
                "conferenceRecord": "conferenceRecords/c1"
            },
        }


class SpaceSession:
    def __init__(self):
        self.url = None

    def get(self, url, params=None, timeout=None):
        self.url = url
        return SpaceResponse()


def test_space_lookup_exposes_active_conference_resource():
    session = SpaceSession()
    client = MeetClient(session, base_url="https://example.test/v2")
    space = client.get_space("spaces/abc-mnop-xyz")
    assert space["activeConference"]["conferenceRecord"] == "conferenceRecords/c1"
    assert session.url.endswith("/spaces/abc-mnop-xyz")
