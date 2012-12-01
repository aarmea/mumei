extern int x, y;
extern int dir;
extern int color;

int wait(int time)
{
  int i;
  i = 0;
  time = time * 100;
  while (i < time) {
    i = i + 1;
  }
  return 0;
}

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

  /* int functions need a return */
  return 0;
}

int step()
{
  moveX(1);
  return 0;
}

int changeColor(int newColor)
{
  color = newColor;
  return 0;
}

/*
int climb();
int dist();
int punch();
*/
