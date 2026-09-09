"""Railway graph model used by the maintenance-planning backend."""

from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf

import networkx as nx


@dataclass(frozen=True)
class TrackSection:
    """A traversable track section between two stations."""

    track_id: str
    start: str
    end: str
    distance_km: float
    speed_limit_kmph: float
    bidirectional: bool = True

    @property
    def travel_minutes(self) -> float:
        if self.distance_km <= 0 or self.speed_limit_kmph <= 0:
            raise ValueError("Track distance and speed must be positive")
        return self.distance_km / self.speed_limit_kmph * 60


class RailwayNetwork:
    """Graph with shortest-time routing and temporary track blocks."""

    def __init__(self) -> None:
        self._tracks: dict[str, TrackSection] = {}
        self._adjacency: dict[str, list[tuple[str, str, float]]] = {}
        self._blocked: set[str] = set()

    def add_track(self, track: TrackSection) -> None:
        if track.track_id in self._tracks:
            raise ValueError(f"Track already exists: {track.track_id}")
        if track.start == track.end:
            raise ValueError("A track must connect two different stations")

        self._tracks[track.track_id] = track
        self._adjacency.setdefault(track.start, []).append(
            (track.end, track.track_id, track.travel_minutes)
        )
        if track.bidirectional:
            self._adjacency.setdefault(track.end, []).append(
                (track.start, track.track_id, track.travel_minutes)
            )

    def block_track(self, track_id: str) -> None:
        self._require_track(track_id)
        self._blocked.add(track_id)

    def unblock_track(self, track_id: str) -> None:
        self._require_track(track_id)
        self._blocked.discard(track_id)

    def route(
        self,
        start: str,
        end: str,
        blocked_tracks: set[str] | None = None,
    ) -> tuple[list[str], float]:
        """Return the fastest available route and travel time."""
        if start == end:
            return [], 0.0
        if start not in self._adjacency or end not in self._adjacency:
            raise ValueError(
                f"Unknown station: {start if start not in self._adjacency else end}"
            )

        blocked = self._blocked | (blocked_tracks or set())
        distances: dict[str, float] = {start: 0.0}
        previous: dict[str, tuple[str, str]] = {}
        queue: list[tuple[float, str]] = [(0.0, start)]

        while queue:
            current_time, station = heappop(queue)
            if current_time > distances[station]:
                continue
            if station == end:
                break

            for next_station, track_id, duration in self._adjacency[station]:
                if track_id in blocked:
                    continue
                candidate = current_time + duration
                if candidate < distances.get(next_station, inf):
                    distances[next_station] = candidate
                    previous[next_station] = (station, track_id)
                    heappush(queue, (candidate, next_station))

        if end not in distances:
            raise ValueError(f"No available route from {start} to {end}")

        route: list[str] = []
        station = end
        while station != start:
            previous_station, track_id = previous[station]
            route.append(track_id)
            station = previous_station
        route.reverse()
        return route, distances[end]

    def _require_track(self, track_id: str) -> None:
        if track_id not in self._tracks:
            raise ValueError(f"Unknown track: {track_id}")


def build_track_network() -> nx.Graph:
    """Return the NetworkX graph expected by the existing backend."""
    graph = nx.Graph()
    graph.add_edge("S1", "S2", weight=15, track_id="S1-S2")
    graph.add_edge("S2", "S3", weight=20, track_id="S2-S3")
    return graph


def build_demo_network() -> RailwayNetwork:
    """Create the A-B-C network used by the RailSync demonstration."""
    network = RailwayNetwork()
    network.add_track(TrackSection("A-B", "A", "B", 10, 20))
    network.add_track(TrackSection("B-C", "B", "C", 15, 20))
    network.add_track(TrackSection("A-C", "A", "C", 30, 20))
    return network
