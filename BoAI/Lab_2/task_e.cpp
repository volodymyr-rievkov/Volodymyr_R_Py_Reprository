#include<bits/stdc++.h>
using namespace std;

char ME, OPP;
string board(16, '.');

struct Result
{
    int outcome;
    int plies;
    Result(int o=0, int p=0): outcome(o), plies(p) {}
};

unordered_map<string, Result> memo;

void assign_players(char p)
{
    ME = p;
    if (p == 'X')
    {
        OPP = 'O';
    }
    else
    {
        OPP = 'X';
    }
}

inline int id(int r, int c) {return r * 4 + c;}

void fill_board()
{
    string row;

    for(int r = 0; r < 4; r++)
    {
        cin >> row;
        for(int c = 0; c < 4; c++)
        {
            board[id(r, c)] = row[c];
        }
    }
}

char find_winner(string &curBoard)
{
    for(int r = 0; r < 4; r++)
    {
        for(int c = 0; c < 4; c++)
        {
            char v = curBoard[id(r, c)];
            if(v == '.') continue;
            if(c + 3 < 4 && curBoard[id(r, c + 1)] == v && curBoard[id(r, c + 2)] == v && curBoard[id(r, c + 3)] == v) return v;
            if(r + 3 < 4 && curBoard[id(r + 1, c)] == v && curBoard[id(r + 2, c)] == v && curBoard[id(r + 3, c)] == v) return v;
            if(c + 3 < 4 && r + 3 < 4 && curBoard[id(r + 1, c + 1)] == v && curBoard[id(r + 2, c + 2)] == v && curBoard[id(r + 3, c + 3)] == v) return v;
            if(c - 3 >= 0 && r + 3 < 4 && curBoard[id(r + 1, c - 1)] == v && curBoard[id(r + 2, c - 2)] == v && curBoard[id(r + 3, c - 3)] == v) return v;        
        }
    }
    return '.';
}

vector<int> find_moves(string &curBoard)
{
    vector<int> moves;
    for(int c = 0; c < 4; c++)
    {
        if(curBoard[id(0, c)] == '.') moves.push_back(c);
    }
    return moves;
}

bool full(string &curBoard)
{
    for(char x : curBoard)
    {
        if(x == '.')
        {
            return false;
        }
    }
    return true;
}

int rankOutcome(int o)
{
    return o == 1 ? 2 : (o == 0 ? 1: 0);
}

Result solve(string &curBoard, char cur)
{
    string key = curBoard + cur;
    if(memo.count(key)) return memo[key];

    char w = find_winner(curBoard);
    if(w != '.')
    {
        return memo[key] = Result(w == ME ? 1: -1, 0);
    }
    if(full(curBoard))
    {
        return memo[key] = Result(0, 0);
    }

    vector<int> moves = find_moves(curBoard);

    bool self = (ME == cur);
    Result best;
    bool first = true;

    for(int c : moves)
    {
        string newBoard = curBoard;
        for(int r = 3; r >= 0; r--)
        {
            if(newBoard[id(r, c)] == '.')
            {
                newBoard[id(r, c)] = cur;
                break;
            }
        }
        char next = (cur == 'X' ? 'O' : 'X');

        Result r = solve(newBoard, next);
        Result val(r.outcome, r.plies + 1);

        if(first)
        {
            best = val;
            first = false;
            continue;
        }

        int rb = rankOutcome(best.outcome);
        int rv = rankOutcome(val.outcome);

        if(self)
        {
            if(rv != rb)
            {
                if(rv > rb) best = val;
            } 
            else if(rb == 2)
            {
                if(val.plies < best.plies) best = val;
            } 
            else if(rb == 1)
            {
                if(val.plies < best.plies) best = val;
            } 
            else 
            {
                if(val.plies > best.plies) best = val;
            }
        } 
        else 
        {
            if(rv != rb)
            {
                if(rv < rb) best = val;
            } 
            else if(rb == 0)
            {
                if(val.plies < best.plies) best = val;
            } 
            else if(rb == 1)
            {
                if(val.plies < best.plies) best = val;
            }
            else 
            {
                if(val.plies > best.plies) best = val;
            }
        }
    }
    return memo[key] = best;
}

int find_best_move(string &curBoard)
{
    vector<int> moves = find_moves(curBoard);

    int bestCol = moves[0];
    Result best;
    bool first = true;

    for(int c : moves)
    {
        string newBoard = curBoard;
        for(int r = 3; r >= 0; r--)
        {
            if(newBoard[id(r, c)] == '.')
            {
                newBoard[id(r, c)] = ME;
                break;
            }
        }
        Result r = solve(newBoard, OPP);
        Result val(r.outcome, r.plies + 1);

        if(first){
            best = val;
            bestCol = c;
            first = false;
            continue;
        }

        int rb = rankOutcome(best.outcome);
        int rv = rankOutcome(val.outcome);

        if(rv != rb){
            if(rv > rb){ best = val; bestCol = c; }
        } else if(rb == 2){
            if(val.plies < best.plies){ best = val; bestCol = c; }
        } else if(rb == 1){
            if(val.plies < best.plies){ best = val; bestCol = c; }
        } else {
            if(val.plies > best.plies){ best = val; bestCol = c; }
        }
    }

    return bestCol;
}

bool play(char t)
{
    while(true)
    {
        if(t == ME)
        {
            if(find_winner(board) != '.' || full(board)) return false;
            int col = find_best_move(board);
            for(int r = 3; r >= 0; r--)
            {
                if(board[id(r, col)] == '.')
                {
                    board[id(r, col)] = ME;
                    break;
                }
            }
        cout << col + 1 << endl;
        cout.flush();
        t = OPP;
        }

        int c;
        if(!(cin >> c)) return false;
        if(c == 0) return false;

        int col = c - 1;
        for(int r = 3; r >= 0; r--)
        {
            if(board[id(r, col)] == '.')
            {
                board[id(r, col)] = t;
                break;
            }
        }
        t = (t == 'X' ? 'O' : 'X');
    }
}

int main()
{
    char p, t;
    cin >> p >> t;

    assign_players(p);
    fill_board();
    if(!play(t))
    {
        return 0;
    }
}
