#pragma once
#include "SharedState.h"
template<typename T>
class Future {
private:
	SharedState<T>* state;

public:
	Future(SharedState<T>* sstate) : state(sstate) {}
	T Get() {
		state->WaitResult();
		return state->Get();
	}
	bool TryGet(T& outValue) {
		return state.TryGet(outValue);
	}
};



