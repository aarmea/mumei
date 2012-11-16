/* Pointers, locals */
/* int main(int a) { int *baz; baz = 0x80; *baz = 0xA5A5; return baz; } */

/* Pointers, globals */
/* extern int *foo; int main(int a) { foo = 0x80; *(foo + 1) = 0xA5A5; return foo; } */

/* Iteration, comparison */
/* int main(int a) { int baz; baz = 3; while (baz < 5) baz = baz + 1; return baz; } */

/* Function declarations, function calls */
/* int f(int a, int b); int main(int a) { return f(0x88, 0x89); } int f(int a, int b) { return a + b; } */

/* Misc. */
extern int foo, *bar;

int g(int x);

int f(int a) {
  int baz;
  baz = 3;
  if (baz < 4)
    foo = 4;
  while (baz < 5)
    baz = baz + 1;
  baz = g(0x80);
  *baz = 0xA5A5;
  return (foo = bar = baz = 1);
  return foo + bar;
}

int g(int x) {
  return x + 1;
}
/**/

