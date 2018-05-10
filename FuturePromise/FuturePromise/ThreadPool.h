#pragma once
#include <map>
#include <Windows.h>

class ThreadPool {
private:
	int numThreads;
	const int maxThreads = 8; //would have be better if it was hardware_concurrency, but C++11 is prohibited

public:
	ThreadPool() {
		numThreads = 0;
		hMutex = CreateMutex(NULL, FALSE, NULL);
	}
	~ThreadPool() {
		CloseHandle(hMutex);
	}
	bool isFull() {
		return numThreads >= maxThreads;
	}
	void addThread() {
		WaitForSingleObject(hMutex, INFINITE);
		++numThreads;
		ReleaseMutex(hMutex);
	}
	void discardThread() {
		WaitForSingleObject(hMutex, INFINITE);
		--numThreads;
		ReleaseMutex(hMutex);
	}
	std::map<unsigned, void*> promises;
	HANDLE hMutex;
};

