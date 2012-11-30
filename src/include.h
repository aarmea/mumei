extern int x, y;
extern int dir;
extern int color;

int moveX(int dist)
{
  int dest;
  dest = x + dist;
  while (x < dest) {
    color = 1;
    dir = 2;
  }
  while (x > dest) {
    color = 2;
    dir = 1;
  }
  color = 0;
  dir = 0;
}

/*
int step();

int climb();
int dist();
int changeColor();
int wait();
int punch();
*/
