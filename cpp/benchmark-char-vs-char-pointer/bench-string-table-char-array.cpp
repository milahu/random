/*

nix-shell -p gcc papi

g++ -lpapi -DUSE_PAPI -std=c++0x -O3 bench-string-table-char-array.cpp -o bench-string-table-char-array

./bench-string-table-char-array



which is faster?

const char  a1[93][7] // char_array = sparse array, padded with zero bytes
const char* a2[]      // char_pointer_array = dense array

spoiler: a1 is faster by 5%, at least in my benchmark ...



a1 needs more memory:

93 * 7 = 651 byte
sizeof(a2) = 232 byte



memory layout:

objdump -s -j .rodata -j .data bench-string-table-char-array



benchmark based on
https://stackoverflow.com/questions/21946447/how-much-performance-difference-when-using-string-vs-char-array/21946709

code based on
https://github.com/NixOS/nix/pull/5512

*/

#include <iostream>
#include <fstream>
#include <string>
#include <stdio.h>
#include "papi.h"
#include <vector>
#include <cmath>

/*
#define TRIALS 10000000
*/
#define TRIALS 1000000



// https://stackoverflow.com/questions/7724448
// note: we use full jump table to make this as fast as possible
// note: we assume valid input. errors should be handled by the nix parser
// 93 * 7 = 651 byte
const char String_showAsJson_replace_array__char_array[93][7] = {
  "\\u0000", "\\u0001", "\\u0002", "\\u0003", "\\u0004", // 0 - 4
  "\\u0005", "\\u0006", "\\u0007", "\\b", "\\t", // 5 - 9
  "\\n", "\\u000b", "\\f", "\\r", "\\u000e", // 10 - 14
  "\\u000f", "\\u0010", "\\u0011", "\\u0012", "\\u0013", // 15 - 19
  "\\u0014", "\\u0015", "\\u0016", "\\u0017", "\\u0018", // 20 - 24
  "\\u0019", "\\u001a", "\\u001b", "\\u001c", "\\u001d", // 25 - 29
  "\\u001e", "\\u001f", " ", "!", "\\\"", // 30 - 34
  "#", "$", "%", "&", "'", // 35 - 39
  "(", ")", "*", "+", ",", // 40 - 44
  "-", ".", "/", "0", "1", // 45 - 49
  "2", "3", "4", "5", "6", // 50 - 54
  "7", "8", "9", ":", ";", // 55 - 59
  "<", "=", ">", "?", "@", // 60 - 64
  "A", "B", "C", "D", "E", // 65 - 69
  "F", "G", "H", "I", "J", // 70 - 74
  "K", "L", "M", "N", "O", // 75 - 79
  "P", "Q", "R", "S", "T", // 80 - 84
  "U", "V", "W", "X", "Y", // 85 - 89
  "Z", "[", "\\\\", // 90 - 92
};

void String_showAsJson__char_array(std::ostream & o, const std::string & s) {
  for (auto c = s.cbegin(); c != s.cend(); c++) {
    if ((std::uint8_t) *c <= 92)
      o << String_showAsJson_replace_array__char_array[(std::uint8_t) *c];
    else
      o << *c;
  }
}



const char* String_showAsJson_replace_array__char_pointer_array[] = {
  "\\u0000", "\\u0001", "\\u0002", "\\u0003", "\\u0004", // 0 - 4
  "\\u0005", "\\u0006", "\\u0007", "\\b", "\\t", // 5 - 9
  "\\n", "\\u000b", "\\f", "\\r", "\\u000e", // 10 - 14
  "\\u000f", "\\u0010", "\\u0011", "\\u0012", "\\u0013", // 15 - 19
  "\\u0014", "\\u0015", "\\u0016", "\\u0017", "\\u0018", // 20 - 24
  "\\u0019", "\\u001a", "\\u001b", "\\u001c", "\\u001d", // 25 - 29
  "\\u001e", "\\u001f", " ", "!", "\\\"", // 30 - 34
  "#", "$", "%", "&", "'", // 35 - 39
  "(", ")", "*", "+", ",", // 40 - 44
  "-", ".", "/", "0", "1", // 45 - 49
  "2", "3", "4", "5", "6", // 50 - 54
  "7", "8", "9", ":", ";", // 55 - 59
  "<", "=", ">", "?", "@", // 60 - 64
  "A", "B", "C", "D", "E", // 65 - 69
  "F", "G", "H", "I", "J", // 70 - 74
  "K", "L", "M", "N", "O", // 75 - 79
  "P", "Q", "R", "S", "T", // 80 - 84
  "U", "V", "W", "X", "Y", // 85 - 89
  "Z", "[", "\\\\", // 90 - 92
};
const std::uint8_t String_showAsJson_replace_array_length__char_pointer_array =
  (std::uint8_t) (sizeof(String_showAsJson_replace_array__char_pointer_array) / sizeof(char*));

void String_showAsJson__char_pointer_array(std::ostream & o, const std::string & s) {
  for (auto c = s.cbegin(); c != s.cend(); c++) {
    if ((std::uint8_t) *c < String_showAsJson_replace_array_length__char_pointer_array)
    //if ((std::uint8_t) *c <= 92)
      o << String_showAsJson_replace_array__char_pointer_array[(std::uint8_t) *c];
    else
      o << *c;
  }
}




class Clock
{
  public:
    typedef long_long time;
    time start;
    Clock() : start(now()){}
    void restart(){ start = now(); }
    time usec() const{ return now() - start; }
    time now() const{ return PAPI_get_real_usec(); }
};


int main()
{
  printf("String_showAsJson_replace_array_length__char_pointer_array = %u should be 93\n", String_showAsJson_replace_array_length__char_pointer_array);

  {
    std::cout << "function test ...\n";
    std::ofstream outputStream("/dev/stdout");
    String_showAsJson__char_array(outputStream, "hello \" world from char_array\n");
    outputStream << '\n';
    String_showAsJson__char_pointer_array(outputStream, "hello \" world from char_pointer_array\n");
    outputStream << '\n';
    std::cout << "function test done\n";
  }

  std::ofstream nullOutputStream("/dev/null", std::ios::binary);
  //std::ofstream nullOutputStream("/dev/null");

  //std::ofstream outputStream("/dev/stdout"); // test

  //int randInt = rand() % 256;         // v1 in the range 0 to 255
  //char randChar = (char) randInt;
  //char randChar = (char) (rand() % 256);

  /*
  double d = 3.14;
  outputStream.write(reinterpret_cast<char*>(&d), sizeof d); // binary output
  outputStream << 123 << "abc" << '\n';                      // text output
  */




  int len = 100;


  
  {
    std::cout << "warmup char_array ...\n";
    for (int i=0;i<TRIALS;++i)
    {
      std::string tmp_s;
      tmp_s.reserve(len);
      for (int k = 0; k < len; k++) {
        char randChar = (char) (rand() % 256);
        tmp_s += randChar;
      }
      String_showAsJson__char_array(nullOutputStream, tmp_s);
    }
    std::cout << "warmup char_array done\n";
  }



  {
    std::cout << "warmup char_pointer_array ...\n";
    for (int i=0;i<TRIALS;++i)
    {
      std::string tmp_s;
      tmp_s.reserve(len);
      for (int k = 0; k < len; k++) {
        char randChar = (char) (rand() % 256);
        tmp_s += randChar;
      }
      String_showAsJson__char_pointer_array(nullOutputStream, tmp_s);
    }
    std::cout << "warmup char_pointer_array done\n";
  }








  int eventSet = PAPI_NULL;
  PAPI_library_init(PAPI_VER_CURRENT);
  if(PAPI_create_eventset(&eventSet)!=PAPI_OK) 
  {
    std::cerr << "Failed to initialize PAPI event" << std::endl;
    return 1;
  }

  Clock clock;


  {
    std::cout << "bench char_array ...\n";

    std::vector<long_long> usecs;

    for (int i=0;i<TRIALS;++i)
    {
      clock.restart();
      // round start

      std::string tmp_s;
      tmp_s.reserve(len);
      for (int k = 0; k < len; k++) {
        char randChar = (char) (rand() % 256);
        tmp_s += randChar;
      }
      String_showAsJson__char_array(nullOutputStream, tmp_s);

      // round done
      usecs.push_back(clock.usec());
    }

    long_long sum = 0;
    for(auto vecIter = usecs.begin(); vecIter != usecs.end(); ++vecIter)
    {
      sum+= *vecIter;
    }

    double average = static_cast<double>(sum)/static_cast<double>(TRIALS);
    std::cout << "Average: " << average << " microseconds" << std::endl;

    //compute variance
    double variance = 0;
    for(auto vecIter = usecs.begin(); vecIter != usecs.end(); ++vecIter)
    {
      variance += (*vecIter - average) * (*vecIter - average);
    }

    variance /= static_cast<double>(TRIALS);
    std::cout << "Variance: " << variance << " microseconds" << std::endl;
    std::cout << "Std. deviation: " << sqrt(variance) << " microseconds" << std::endl;
    double CI = 1.96 * sqrt(variance)/sqrt(static_cast<double>(TRIALS));
    std::cout << "95% CI: " << average-CI << " usecs to " << average+CI << " usecs" << std::endl;

    std::cout << "bench char_array done\n";
  }

  std::cout << "\n##########################################\n";

  {
    std::cout << "bench char_pointer_array ...\n";

    std::vector<long_long> usecs;

    for (int i=0;i<TRIALS;++i)
    {
      clock.restart();
      // round start

      std::string tmp_s;
      tmp_s.reserve(len);
      for (int k = 0; k < len; k++) {
        char randChar = (char) (rand() % 256);
        tmp_s += randChar;
      }
      String_showAsJson__char_pointer_array(nullOutputStream, tmp_s);

      // round done
      usecs.push_back(clock.usec());
    }

    long_long sum = 0;
    for(auto vecIter = usecs.begin(); vecIter != usecs.end(); ++vecIter)
    {
      sum+= *vecIter;
    }

    double average = static_cast<double>(sum)/static_cast<double>(TRIALS);
    std::cout << "Average: " << average << " microseconds" << std::endl;

    //compute variance
    double variance = 0;
    for(auto vecIter = usecs.begin(); vecIter != usecs.end(); ++vecIter)
    {
      variance += (*vecIter - average) * (*vecIter - average);
    }

    variance /= static_cast<double>(TRIALS);
    std::cout << "Variance: " << variance << " microseconds" << std::endl;
    std::cout << "Std. deviation: " << sqrt(variance) << " microseconds" << std::endl;
    double CI = 1.96 * sqrt(variance)/sqrt(static_cast<double>(TRIALS));
    std::cout << "95% CI: " << average-CI << " usecs to " << average+CI << " usecs" << std::endl;

    std::cout << "bench char_pointer_array done\n";
  }

}

