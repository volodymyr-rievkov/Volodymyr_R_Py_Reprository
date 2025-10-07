#include <bits/stdc++.h>
using namespace std;

const int INF = 1e9;

struct Point {
    int r, c;
};

int bfs(const vector<string>& room, Point start, Point goal) {
    int n = room.size(), m = room[0].size();
    queue<pair<int,int>> q;
    vector<vector<int>> dist(n, vector<int>(m, INF));

    dist[start.r][start.c] = 0;
    q.push({start.r, start.c});

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    while (!q.empty()) {
        auto [r, c] = q.front(); q.pop();
        if (r == goal.r && c == goal.c) return dist[r][c];

        for (int i = 0; i < 4; ++i) {
            int nr = r + dr[i], nc = c + dc[i];
            if (nr >= 0 && nr < n && nc >= 0 && nc < m && dist[nr][nc] == INF) {
                dist[nr][nc] = dist[r][c] + 1;
                q.push({nr, nc});
            }
        }
    }
    return INF;
}

vector<vector<int>> build_distance_matrix(const vector<string>& room, const vector<Point>& points) {
    int k = points.size();
    vector<vector<int>> dist(k, vector<int>(k, INF));

    for (int i = 0; i < k; ++i)
        for (int j = 0; j < k; ++j)
            if (i != j)
                dist[i][j] = bfs(room, points[i], points[j]);

    return dist;
}

int tsp_with_cleaning(const vector<vector<int>>& dist) {
    int k = dist.size();
    int full_mask = (1 << k);
    vector<vector<int>> dp(full_mask, vector<int>(k, INF));
    dp[1][0] = 0; 

    for (int mask = 1; mask < full_mask; ++mask) {
        for (int i = 0; i < k; ++i) {
            if (!(mask & (1 << i)) || dp[mask][i] == INF) continue;

            for (int j = 1; j < k; ++j) { 
                if (mask & (1 << j)) continue;
                int next = mask | (1 << j);
                dp[next][j] = min(dp[next][j], dp[mask][i] + dist[i][j] + 1);
            }
        }
    }

    int ans = INF;
    for (int i = 0; i < k; ++i)
        ans = min(ans, dp[full_mask - 1][i]);
    return ans;
}

int solve() 
{
    int n, m;
    cin >> n >> m;
    vector<string> room(n);
    for (auto &row : room) cin >> row;

    vector<Point> points = {{0, 0}};
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < m; ++j)
            if (room[i][j] == '*')
                points.push_back({i, j});

    if (points.size() == 1) return 0;

    auto dist = build_distance_matrix(room, points);
    return tsp_with_cleaning(dist);
}

int main() 
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cout << solve() << "\n";
    return 0;
}
