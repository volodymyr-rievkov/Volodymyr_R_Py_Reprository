#include <bits/stdc++.h>
using namespace std;

const int SEED = 42;
mt19937 rng(SEED);
const int PARTICLES_COUNT = 1500;
const double PARTICLE_WEIGHT = 1.0 / PARTICLES_COUNT;
const double ND_STD = 0.1;
const double INF = 1e9;
const int RAYS_PER_FILTER = 20;
const int RAYS_PER_OPT = 80;
const double WEIGHT_THRESHOLD = 1e-50;
const double PI = acos(-1.0);

struct Point {
    double x, y;
};

struct Particle {
    Point p;
    double weight;
};

int N, M, K;
double S1, Sx, Sy;
vector<Point> polygon;
vector<Particle> particles;
vector<double> scan;

void findPolygonExtents(double& minX, double& maxX, double& minY, double& maxY) {
    minX = minY = INF;
    maxX = maxY = -INF;
    for (const auto& p : polygon) {
        if (p.x < minX) minX = p.x;
        if (p.x > maxX) maxX = p.x;
        if (p.y < minY) minY = p.y;
        if (p.y > maxY) maxY = p.y;
    }
}

bool isInside(double x, double y) {
    bool inside = false;
    for (int i = 0, j = N - 1; i < N; j = i++) {
        if (((polygon[i].y > y) != (polygon[j].y > y)) &&
            (x < (polygon[j].x - polygon[i].x) * (y - polygon[i].y) / (polygon[j].y - polygon[i].y) + polygon[i].x)) {
            inside = !inside;
        }
    }
    return inside;
}

void setParticles(vector<Particle>& particles) {
    double minX, maxX, minY, maxY;
    findPolygonExtents(minX, maxX, minY, maxY);
    uniform_real_distribution<double> Xdistrib(minX, maxX);
    uniform_real_distribution<double> Ydistrib(minY, maxY);
    int count = 0;
    while (count < PARTICLES_COUNT) {
        double rx = Xdistrib(rng);
        double ry = Ydistrib(rng);
        if (isInside(rx, ry)) {
            particles[count] = {{rx, ry}, PARTICLE_WEIGHT};
            count++;
        }
    }
}

vector<Particle> initParticles(bool isKnown, double startX, double startY) {
    vector<Particle> particles(PARTICLES_COUNT);
    if (isKnown) {
        normal_distribution<double> Xdistrib(startX, ND_STD);
        normal_distribution<double> Ydistrib(startY, ND_STD);
        for (int i = 0; i < PARTICLES_COUNT; i++) {
            particles[i] = {{Xdistrib(rng), Ydistrib(rng)}, PARTICLE_WEIGHT};
        }
    } else {
        setParticles(particles);
    }
    return particles;
}

double findRayDist(double x, double y, double angle) {
    double minDist = INF;
    double dx = cos(angle);
    double dy = sin(angle);
    for (int i = 0; i < N; i++) {
        Point p1 = polygon[i];
        Point p2 = polygon[(i + 1) % N];
        double v1x = p1.x - x;
        double v1y = p1.y - y;
        double v2x = p2.x - p1.x;
        double v2y = p2.y - p1.y;
        double det = v2x * dy - v2y * dx;
        if (abs(det) < 1e-9) continue;
        double t = (v2x * v1y - v2y * v1x) / det;
        double u = (dx * v1y - dy * v1x) / det;
        if (t > 0 && u >= 0 && u <= 1) 
        {
            if (t < minDist) minDist = t;
        }
    }
    return minDist;
}

void updateWeights(vector<Particle>& particles, const vector<double>& scan) {
    double totalWeight = 0;
    int step = max(1, K / RAYS_PER_FILTER);
    double eff_S1 = max(S1, 0.03);
    double denom = 2.0 * eff_S1 * eff_S1;
    for (auto& p : particles) {
        Point point = p.p;
        if (!isInside(point.x, point.y)) {
            p.weight = 0;
            continue;
        }
        double errorSum = 0;
        int checks = 0;
        for (int i = 0; i < K; i += step) {
            double angle = i * (2 * PI / K);
            double dist = findRayDist(point.x, point.y, angle);
            double diff = scan[i] - dist;
            double errorBound = 2.0;
            if (diff > errorBound) diff = errorBound;
            if (diff < -errorBound) diff = -errorBound;
            errorSum += (diff * diff);
            checks++;
        }
        if (checks > 0) p.weight = exp(-errorSum / (denom * checks));
        else p.weight = 0;
        if (isnan(p.weight)) p.weight = 0;
        totalWeight += p.weight;
    }
    if (totalWeight < WEIGHT_THRESHOLD) {
        setParticles(particles);
    } else {
        for (auto& p : particles) p.weight /= totalWeight;
    }
}

void resampleParticles(vector<Particle>& particles) {
    double sqSum = 0;
    for (const auto& p : particles) sqSum += p.weight * p.weight;
    double neff = 1.0 / sqSum;

    if (neff > PARTICLES_COUNT / 2.0) return;
    vector<Particle> newParticles;
    newParticles.reserve(PARTICLES_COUNT);
    double r = uniform_real_distribution<double>(0, PARTICLE_WEIGHT)(rng);
    double c = particles[0].weight;
    int i = 0;
    for (int m = 0; m < PARTICLES_COUNT; m++) 
    {
        double U = r + m * PARTICLE_WEIGHT;
        while (U > c && i < PARTICLES_COUNT - 1) 
        {
            i++;
            c += particles[i].weight;
        }
        Particle p = particles[i];
        p.weight = PARTICLE_WEIGHT;
        newParticles.push_back(p);
    }
    particles = newParticles;
}

void predictNoise(vector<Particle>& particles, double dx, double dy) {
    normal_distribution<double> noiseX(0, Sx);
    normal_distribution<double> noiseY(0, Sy);
    for (auto& p : particles) {
        p.p.x += dx + noiseX(rng);
        p.p.y += dy + noiseY(rng);
    }
}

bool readInput() {
    if (!(cin >> N)) return false;
    polygon.resize(N);
    for (int i = 0; i < N; i++) {
        cin >> polygon[i].x >> polygon[i].y;
    }
    cin >> M >> K;
    scan.resize(K);
    cin >> S1 >> Sx >> Sy;
    bool isKnown;
    cin >> isKnown;
    double startX = 0, startY = 0;
    if (isKnown) cin >> startX >> startY;
    particles = initParticles(isKnown, startX, startY);
    double dx, dy;
    for (int step = 0; step <= M; step++) {
        for (int i = 0; i < K; i++) cin >> scan[i];
        updateWeights(particles, scan);
        if (step < M) {
            resampleParticles(particles);
            cin >> dx >> dy;
            predictNoise(particles, dx, dy);
        }
    }
    return true;
}

Point estimatePos(vector<Particle>& particles) {
    double x = 0, y = 0;
    for (const auto& p : particles) 
    {
        x += p.p.x * p.weight;
        y += p.p.y * p.weight;
    }
    return {x, y};
}

double calculateError(double x, double y, const vector<double>& scan, int K) {
    if (!isInside(x, y)) return 1e18;
    double error = 0;
    int step = max(1, K / RAYS_PER_OPT);
    double errorBound = 5.0;
    for (int i = 0; i < K; i += step) {
        double angle = i * (2 * PI / K);
        double sim = findRayDist(x, y, angle);
        double diff = scan[i] - sim;
        if (diff > errorBound) diff = errorBound;
        if (diff < -errorBound) diff = -errorBound;
        error += diff * diff;
    }
    return error;
}

Point optimizePos(Point start, const vector<double>& scan, int K) {
    double x = start.x;
    double y = start.y;
    double currentErr = calculateError(x, y, scan, K);

    double step = 0.05;
    double minStep = 0.0001;
    while (step > minStep) {
        bool improved = false;

        double candidates[4][2] = {{step, 0}, {-step, 0}, {0, step}, {0, -step}};

        for (auto& dir : candidates) {
            double nx = x + dir[0];
            double ny = y + dir[1];
            double newErr = calculateError(nx, ny, scan, K);

            if (newErr < currentErr) {
                x = nx;
                y = ny;
                currentErr = newErr;
                improved = true;
                break;
            }
        }

        if (!improved) {
            step *= 0.5;
        }
    }
    return {x, y};
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    if (!readInput()) return 0;
    Point pfRes = estimatePos(particles);
    Point optRes = optimizePos(pfRes, scan, K);
    cout << fixed << setprecision(5) << optRes.x << " " << optRes.y << endl;

    return 0;
}