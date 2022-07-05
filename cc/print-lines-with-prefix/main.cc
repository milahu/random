/*
print lines with prefix

example output

g++ -g main.cc -o main && ./main

process 2981423: a
process 2981423: b
process 2981423: 1
process 2981423: 2
process 2981423: a
process 2981423: b
process 2981423: a
process 2981423: b
*/

#include <iostream>

#include <cassert> // assert

#include <sys/types.h> // getpid
#include <unistd.h> // getpid

// https://stackoverflow.com/a/27336473/10440128
class prefixbuf
    : public std::streambuf
{
    std::string     prefix;
    std::streambuf* sbuf;
    bool            need_prefix;

    int sync() {
        return this->sbuf->pubsync();
    }
    int overflow(int c) {
        if (c != std::char_traits<char>::eof()) {
            if (this->need_prefix
                && !this->prefix.empty()
                && this->prefix.size() != (long unsigned int) this->sbuf->sputn(&this->prefix[0], this->prefix.size())) {
                return std::char_traits<char>::eof();
            }
            this->need_prefix = c == '\n';
        }
        return this->sbuf->sputc(c);
    }
public:
    prefixbuf(std::string const& prefix, std::streambuf* sbuf)
        : prefix(prefix)
        , sbuf(sbuf)
        , need_prefix(true) {
    }
};

class oprefixstream
    : private virtual prefixbuf
    , public std::ostream
{
public:
    oprefixstream(std::string const& prefix, std::ostream& out)
        : prefixbuf(prefix, out.rdbuf())
        , std::ios(static_cast<std::streambuf*>(this))
        , std::ostream(static_cast<std::streambuf*>(this)) {
    }
};

class MainClass
{
  private:
    const char* s;
    oprefixstream *oprefixstream_;
  public:
    MainClass()
      : s("a\nb\n")
    {
      char line_prefix[100];
      pid_t pid = getpid();
      assert(snprintf(line_prefix, 100, "process %d: ", pid) < 100);

      oprefixstream_ = new oprefixstream(line_prefix, std::cout);
    }
    void Print() {
      *oprefixstream_ << s;
      *oprefixstream_ << "1\n2\n";
      (*oprefixstream_).write(&s[0], 4);
      oprefixstream_->write(&s[0], 4);
    }
};

int main()
{
    MainClass m;
    m.Print();
}
