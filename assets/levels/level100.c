extern int x, y;
extern int dir;
extern int color;

int main ()
{
  while ( 1 )
  {
    while ( x < 5 ) {
      color = 1;
      dir = 2;
    }

    while ( x > 2 ) {
      color = 2;
      dir = 1;
    }
  }

  return 0;
}
