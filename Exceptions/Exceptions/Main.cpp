#include "setjmp.h"
#include <iostream>

enum errors { Bad_1 = 1, Bad_2, Bad_3} err;

struct base_type {
	base_type();
	virtual ~base_type();
	base_type* prev;
};

struct try_section {
	try_section();
	~try_section();
	jmp_buf buf;
	try_section* prev_section;
	base_type* section_stack;
	void clear_stack() {
		while (NULL != section_stack)
		{
			base_type *tmp = section_stack;
			section_stack = section_stack->prev;
			tmp ->~base_type();
		}
	}
};

try_section* try_sections = NULL;

base_type::base_type() {
	if (NULL != try_sections)
	{
		prev = try_sections->section_stack;
		try_sections->section_stack = this;
	}
}

base_type::~base_type() {
	//delFromStack();
}


try_section::try_section() {
	section_stack = NULL;
	prev_section = try_sections;
	try_sections = this;
}

try_section::~try_section() {
	try_sections = prev_section;
}

int throw_ex(int err);

#define TRY { \
try_section __sl; \
int __exc = setjmp(__sl.buf); \
if (__exc == 0) 

#define CATCH(exc) \
 else if (__exc == exc)

#define END \
 else { \
throw_ex(__exc); \
} \
}

#define THROW(exc) \
throw_ex (exc);

#define RETHROW \
throw_ex(__exc);

int pop_slice() {
	try_section* sl = try_sections;
	if (NULL == sl) {
		std::abort();
	}
	try_sections = sl->prev_section;
	return 0;
}

int throw_ex(int err) {
	try_section* top_section = try_sections;
	top_section->clear_stack();
	pop_slice();
	longjmp(top_section->buf, err);
	return 0;
}

class my_int : public base_type {
	int value;
public:
	my_int(int _value) { 
		value = _value; 
		std::cout << "my_int() " << value << std::endl;
	};
	~my_int() { 
		std::cout << "~my_int() " << value << std::endl;
	};
};
int main()
{
	TRY{
		my_int a(0);
		std::cout << "KEK";
		THROW(1)
	}
		CATCH(1){
			my_int b(1);
			std::cout << "LOL";
		}
	END
		long a;
	std::cin >> a;
		return 0;
}