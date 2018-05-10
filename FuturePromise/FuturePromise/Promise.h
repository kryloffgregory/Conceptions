#pragma once
#include "Future.h"
template<typename T>
class Promise {
public:
	SharedState<T>* state;

	Promise() : state(new SharedState<T>()) {}
	Future<T> GetFuture() {
		return Future<T>(state);
	}
	void SetValue(T const& value) {
		state->setValue(value);
	}
	void SetException(std::exception* exc) {
		state->setException(exc);
	}
};
