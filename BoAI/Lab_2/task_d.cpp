#include <bits/stdc++.h>
using namespace std;

int N, K;
vector<long long> xs, ys;
vector<long long> cx, cy;
vector<int> assignV;
vector<long long> sumX, sumY, countV;

void read_input()
{
    cin >> N >> K;
    xs.resize(N); ys.resize(N); assignV.resize(N);
    cx.resize(K); cy.resize(K); countV.resize(K); sumX.resize(K); sumY.resize(K);

    for(int i = 0; i < N; i++)
    {
        cin >> xs[i] >> ys[i];
    }

    for(int i = 0; i < K; i++)
    {
        int p; cin >> p; p--;
        cx[i] = xs[p]; cy[i] = ys[p];
    }

}

void assign_points()
{
    fill(sumX.begin(), sumX.end(), 0);
    fill(sumY.begin(), sumY.end(), 0);
    fill(countV.begin(), countV.end(), 0);

    for(int i = 0; i < N; i++)
    {
        long long px = xs[i], py = ys[i];
        int best = 0;
        long long dx = px - cx[0], dy = py - cy[0];
        long long bestD = dx*dx + dy*dy;

        for(int c = 1; c < K; c++)
        {
            dx = px - cx[c]; dy = py - cy[c];
            long long d = dx*dx + dy*dy;

            if(bestD > d)
            {
                bestD = d;
                best = c;
            }
        }
        assignV[i] = best;
        sumX[best] += px;
        sumY[best] += py;
        countV[best]++;
    }
}

void update_centroids()
{
    for(int c = 0; c < K; c++)
    {
        if(countV[c] == 0)
        {
            cx[c] = 0; cy[c] = 0;
        }
        else 
        {
            cx[c] = sumX[c] / countV[c];
            cy[c] = sumY[c] / countV[c];
        }
    }
}

void run_kmeans()
{
    for(int i = 0; i < 100; i++)
    {
        assign_points();
        update_centroids();
    }
}

void print_output()
{
    for(int i = 0; i < N; i++)
    {
        cout << assignV[i] + 1 << endl;
    }
}

int main()
{
    read_input();
    run_kmeans();
    print_output();
}

// O(N + K + (N * K + K) * 100) = O(100 * N * K)