#include <bits/stdc++.h>
using namespace std;

const int N = 5;
const int CELLS = N * N;
const int NEGAMAX_BOUND = 1000000000;

string board(CELLS, '.');

unordered_map<uint64_t, int> memo;

inline int id(int r, int c) { return r * N + c; } 

void fill_board()
{
    for(int r = 0; r < N; r++)
    {
        string s; cin >> s;
        for(int c = 0; c < N; c++)
        {
            board[id(r, c)] = s[c];
        }
    }
}

char getCurrentPlayer()
{
    int x = 0, o = 0;
    for(int i = 0; i < CELLS; i++)
    {
        if(board[i] == 'X') x++;
        else if(board[i] == 'O') o++;
    }
    return (x == o) ? 'X' : 'O';
}

bool hasWon(char p) {
    for (int r = 0; r < N; ++r) {
        for (int c = 0; c < N; ++c) {
            if (c + 3 < N &&
                board[id(r,c)] == p &&
                board[id(r,c+1)] == p &&
                board[id(r,c+2)] == p &&
                board[id(r,c+3)] == p) return true;
            if (r + 3 < N &&
                board[id(r,c)] == p &&
                board[id(r+1,c)] == p &&
                board[id(r+2,c)] == p &&
                board[id(r+3,c)] == p) return true;
            if (r + 3 < N && c + 3 < N &&
                board[id(r,c)] == p &&
                board[id(r+1,c+1)] == p &&
                board[id(r+2,c+2)] == p &&
                board[id(r+3,c+3)] == p) return true;
            if (r + 3 < N && c - 3 >= 0 &&
                board[id(r,c)] == p &&
                board[id(r+1,c-1)] == p &&
                board[id(r+2,c-2)] == p &&
                board[id(r+3,c-3)] == p) return true;
        }
    }
    return false;
}

bool isFull() {
    for (int c = 0; c < N; ++c) {
        if (board[id(0,c)] == '.') return false;
    }
    return true;
}

inline uint64_t makeKey64(char cur) {
    uint64_t xmask = 0, omask = 0;
    for (int r = 0; r < N; ++r) 
    {
        for (int c = 0; c < N; ++c) 
        {
            int idx = id(r,c);
            if (board[idx] == 'X') xmask |= (1ULL << idx);
            else if (board[idx] == 'O') omask |= (1ULL << idx);
        }
    }
    uint64_t side = (cur == 'X') ? 0ULL : 1ULL;
    return xmask | (omask << 25) | (side << 50);
}

vector<int> find_cols()
{
    vector<int> cols;
    for (int c = 0; c < N; c++) 
    {
        if (board[id(0,c)] == '.') cols.push_back(c);
    }
    return cols;
}

int placePiece(int col, char p)
{
    for(int r = N - 1; r >= 0; r--)
    {
        if(board[id(r, col)] == '.')
        {
            board[id(r, col)] = p;
            return r;
        }
    }
    return -1;
}

void removePiece(int col, int row)
{
    if(row >= 0) board[id(row, col)] = '.';
}

bool wouldWin(char p, int col)
{
    if(board[id(0, col)] != '.') return false;
    int row = placePiece(col, p);
    bool w = hasWon(p);
    removePiece(col, row);
    return w;
}

bool oppHasImmediateWin(char opp) 
{
    for (int c = 0; c < N; ++c) 
    {
        if (board[id(0,c)] == '.' && wouldWin(opp, c)) return true;
    }
    return false;
}

int negamaxSearch(int alpha, int beta)
{
    char me = getCurrentPlayer();
    char opp = (me == 'X') ? 'O' : 'X';

    // immediate win/loss/draw conditions
    bool meWin = hasWon(me);
    bool oppWin = hasWon(opp);
    if(meWin && oppWin) return 0; // both won → draw
    if(meWin) return 1;            // current player wins
    if(oppWin) return -1;          // opponent wins
    if(isFull()) return 0;         // board full → draw

    // generate memo key
    uint64_t key = makeKey64(me);
    if(auto it = memo.find(key); it != memo.end()) return it->second;

    // get available columns
    vector<int> cols = find_cols();

    // check for immediate winning move
    for(int c : cols)
    {
        if(wouldWin(me, c))
        {
            memo[key] = 1;  // memoize winning move
            return 1;
        }
    }

    // check opponent's immediate threats
    vector<int> oppWinsNow;
    for(int c : cols) if (wouldWin(opp, c)) oppWinsNow.push_back(c);

    if(oppWinsNow.size() >= 2) 
    {
        memo[key] = -1; // cannot block multiple threats → lose
        return -1;
    }

    if(oppWinsNow.size() == 1)
        cols = { oppWinsNow[0] }; // must block this column

    // score columns to prioritize center
    auto scoreCol = [](int c) 
    {
        static const int pref[N] = {2,1,3,0,4};
        for (int i = 0; i < N; ++i) if(pref[i] == c) return 4 - i;
        return 0;
    };
    sort(cols.begin(), cols.end(), [&](int a, int b){ return scoreCol(a) > scoreCol(b); });

    // check if all moves are immediately bad
    bool allBad = true;
    for(int c : cols)
    {
        int r = placePiece(c, me);
        bool bad = oppHasImmediateWin(opp) && !hasWon(me);
        removePiece(c, r);
        if(!bad) { allBad = false; break; }
    }
    if(allBad) 
    {
        memo[key] = -1; // all moves lead to loss
        return -1;
    }

    int best = -2;   // worse than any possible outcome
    bool cut = false; // alpha-beta cut flag

    for(int c : cols)
    {
        int r = placePiece(c, me);
        bool givesOppInstant = oppHasImmediateWin(opp);
        int val;
        if(givesOppInstant && !hasWon(me)) 
            val = -1; // immediate loss
        else 
            val = -negamaxSearch(-beta, -alpha); // recursive call for opponent
        removePiece(c, r); // undo move

        if(val > best) best = val;       // update best score
        if(val > alpha) alpha = val;     // update alpha
        if(alpha >= beta) { cut = true; break; } // prune branch
    }

    if(best == -2) best = 0;            // no move found → draw
    if(!cut || best == 1) memo[key] = best; // store in memo

    return best; // return best achievable score
}

bool play(int T)
{
    while(T--)
    {
        fill_board();
        memo.clear();
        memo.reserve(1 << 16);

        int res = negamaxSearch(-NEGAMAX_BOUND, NEGAMAX_BOUND);

        if(res > 0) cout << "WIN\n";
        else if(res < 0) cout << "LOSE\n";
        else cout << "DRAW\n";
    }
    return true;
}

int main()
{
    int T;
    if(!(cin >> T)) return 0;
    play(T);
}
