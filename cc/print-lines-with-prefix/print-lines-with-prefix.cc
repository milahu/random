/*
print lines with prefix

example output

g++ -g print-lines-with-prefix.cc -o print-lines-with-prefix && ./print-lines-with-prefix

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

//#include <stdio.h> // stdout

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
    const char *s;
    char line_prefix_[32];
    char *line_prefix_ptr_;
    //std::string line_prefix_string_;
    oprefixstream *oprefixstream_;
  public:
    MainClass()
      : s("a\nb\n")
    {
      pid_t pid = getpid();

      assert(snprintf(line_prefix_, 32, "pid %d: ", pid) < 32);
      printf("line_prefix_ = '%s'\n", line_prefix_);

      line_prefix_ptr_ = (char *) malloc(32);
      snprintf(line_prefix_ptr_, 32, "pid %d: ", pid);
      printf("line_prefix_ptr_ = '%s'\n", line_prefix_ptr_);

      oprefixstream_ = new oprefixstream(line_prefix_, std::cout);
      //oprefixstream_ = new oprefixstream(line_prefix, std::cout);
      //oprefixstream_ = new oprefixstream(line_prefix, std::cerr);
    }
    void Print() {
      *oprefixstream_ << s;
      *oprefixstream_ << "1\n2\n";
      (*oprefixstream_).write(&s[0], 4);
      oprefixstream_->write(&s[0], 4);
      char a[10];
      a[0] = 'a';
      a[1] = 's';
      a[2] = 'd';
      a[3] = 'f';
      a[4] = 0;
      oprefixstream_->write(a, 4);
      oprefixstream_->flush();
    }
};

int main()
{
    MainClass m;
    m.Print();
}
