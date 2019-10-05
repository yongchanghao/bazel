//
// Created by schureed on 19-10-5.
//

#include <cstdio>
#include "protos/test.pb.h"

int main() {
  Message t;
  t.set_name("ok");
  printf("%s\n", t.name().c_str());
}