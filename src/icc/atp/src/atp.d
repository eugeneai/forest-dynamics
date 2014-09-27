module prisnif;

import pyd.pyd;
import std.stdio;
//extern (C) void PydMain () {
//  module_init();
//}

void hello_func() {
  writefln("Hello, world!");
}

extern (C) void PydMain() {
  def!(hello_func)();
  module_init();
}
