#include "Future.h"
#include "Promise.h"
#include "SharedState.h"
#include "ThreadPool.h"
#include <iostream>
#include <Windows.h>
#include <process.h>
#include <functional>

template<typename T>
unsigned __stdcall execProcess(void* params) {
	std::function<T()>* func = (std::function<T()>*) params;
	Promise<T>* promise = (Promise<T>*) pool.promises[GetCurrentThreadId()];
	T res = (*func)();
	promise->SetValue(res);
	WaitForSingleObject(promise->state->hGotValue, INFINITE);
	pool.discardThread();
	WaitForSingleObject(pool.hMutex, INFINITE);
	free(pool.promises[GetCurrentThreadId()]);
	pool.promises.erase(GetCurrentThreadId());
	ReleaseMutex(pool.hMutex);
	CloseHandle(GetCurrentThread());
	_endthreadex(0);
	return 0;
}

ThreadPool pool;


template<typename T>
Future<T> async(std::function<T(void)>* func, bool synchronized = 0) {

	if (synchronized || pool.isFull()) {
		Promise<T> pr;
		Future<T> result = pr.GetFuture();
		pr.SetValue((*func)());
		return result;
	} else {
		pool.addThread();
		unsigned threadID;
		HANDLE hThread = (HANDLE)_beginthreadex(NULL, 0, &execProcess<T>, (void*)func, 0, &threadID);
		WaitForSingleObject(pool.hMutex, INFINITE);
		pool.promises[threadID] = new Promise<T>();
		ReleaseMutex(pool.hMutex); Promise<T>* promise = (Promise<T>*) pool.promises[threadID];
		return promise->GetFuture();
	}

}

int sqr(const int arg) {
	return arg * arg;
}

int Counter;

unsigned __stdcall SecondThreadFunc(void* args)
{
	Future<int>* f = (Future<int>*) args;
	std::cout << "In SecondThreadFunc " << f->Get() << std::endl;
	CloseHandle(GetCurrentThread());
	_endthreadex(0);
	return 0;
}

int main() {

	
	std::cout << "First example\n";
	
	Promise<int> promise1;
	Future<int> check = promise1.GetFuture();
	promise1.SetValue( sqr( 10 ) );
	int res = check.Get();
	if( res == 100)	std::cout << "Success\n";
		else std::cout << "Error\n";
	std::cout << "----------------------------------------\n";
	


	std::cout << "Second example\n";
	Promise<int> promise2;
	Future<int> check2 = promise2.GetFuture();
	unsigned threadID;
	HANDLE hThread = ( HANDLE ) _beginthreadex( NULL, 0, &SecondThreadFunc, &check2, 0, &threadID );
	promise2.SetValue( 7 );
	WaitForSingleObject( hThread, INFINITE );
	CloseHandle( hThread );
	std::cout << "----------------------------------------\n";


	std::cout << "Third example\n";
	std::function<int(void)> sqr1 = std::bind(sqr, 9);
	std::function<int(void)> sqr2 = std::bind(sqr, 13);
	std::function<int(void)> sqr3 = std::bind(sqr, 21);
	Future<int> future1 = async<int>(&sqr1, 0);
	Future<int> future2 = async<int>(&sqr2, 0);
	Future<int> future3 = async<int>(&sqr3, 1);
	std::cout << "Got values: " << future1.Get() << ' ' << future2.Get() << ' ' << future3.Get() << std::endl;
	std::cout << "----------------------------------------\n";
	int l;
	std::cin >> l;
	return 0;
}