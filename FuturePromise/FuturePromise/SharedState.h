#pragma once
#include <exception>
#include <Windows.h>
template <typename T>
class SharedState {
public:
	SharedState();
	SharedState(const SharedState<T>& other);
	~SharedState();
	void WaitResult();
	T Get();
	bool TryGet(T& outValue);

	void setValue(const T _value);
	void setException(const std::exception& exc);

	HANDLE hGotValue;
private:
	T value;
	std::exception* error;
	bool isReady;
	bool wasException;

	HANDLE hEvent;
	HANDLE hMutex;
};

template<typename T>
SharedState<T>::SharedState() {
	hMutex = CreateMutex(NULL, FALSE, NULL);
	isReady = false;
	wasException = false;
	hEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
	hGotValue = CreateEvent(NULL, FALSE, FALSE, NULL);
}

template<typename T>
SharedState<T>::SharedState(const SharedState<T>& other) {
	*this = other;
	hMutex = CreateMutex(NULL, FALSE, NULL);
	hGotValue = CreateEvent(NULL, FALSE, FALSE, NULL);
}

template<typename T>
SharedState<T>::~SharedState() {
	CloseHandle(hMutex);
	CloseHandle(hGotValue);
	CloseHandle(hEvent);
}

template<typename T>
void SharedState<T>::WaitResult() {
	WaitForSingleObject(hEvent, INFINITE);
}

template<typename T>
T SharedState<T>::Get() {
	WaitForSingleObject(hMutex, INFINITE);
	if (isReady) {
		ReleaseMutex(hMutex);
		T res = value;
		isReady = false;
		wasException = false;
		SetEvent(hGotValue);
		return res;
	}
	if (wasException) {
		isReady = false;
		wasException = false;
		ReleaseMutex(hMutex);
		SetEvent(hGotValue);
		throw *error;
	}
	ReleaseMutex(hMutex);
	throw std::runtime_error("Cannot get value");
}

template<typename T>
bool SharedState<T>::TryGet(T& outValue) {
	WaitForSingleObject(hMutex, 0);
	if (isReady) {
		outValue = value;
		isReady = false;
		wasException = false;
		ReleaseMutex(hMutex);
		SetEvent(hGotValue);
		return true;
	} else {
		ReleaseMutex(hMutex);
		return false;
	}
}

template<typename T>
void SharedState<T>::setValue(const T _value) {
	DWORD res = WaitForSingleObject(hMutex, INFINITE);
	if (res != WAIT_OBJECT_0) {
		throw std::runtime_error("Error occured");
	} else {
		value = _value;
		isReady = true;
		ReleaseMutex(hMutex);
		SetEvent(hEvent);
	}
}

template<typename T>
void SharedState<T>::setException(const std::exception& exc) {
	if (WaitForSingleObject(hMutex, 0) != WAIT_OBJECT_0) {
		throw std::runtime_error("Error occured");
	} else {
		error = exc;
		wasException = true;
		ReleaseMutex(hMutex);
		SetEvent(hEvent);
	}
}
