#include <iostream>
#include <cstdint>

const uint32_t TRAIL_MAX = (1U << 18) - 1;

struct Trail18 {
    uint32_t val : 18;

    Trail18() : val(0) {}
    Trail18(uint32_t v) : val(v & ((1U << 18) - 1)) {}

    uint32_t get() const { return val; }
    void set(uint32_t v) { val = v & ((1U << 18) - 1); }

    Trail18& operator=(uint32_t v) { set(v); return *this; }
    operator uint32_t() const { return get(); }

    Trail18& operator+=(uint32_t v) {
        uint32_t new_val = get() + v;
        set((new_val > TRAIL_MAX) ? TRAIL_MAX : new_val);
        return *this;
    }
};

int main() {
    Trail18 t;
    
    std::cout << "Initial value: " << t.get() << std::endl;
    
    t = 100;
    std::cout << "After setting 100: " << t.get() << std::endl;
    
    t += 255;
    std::cout << "After += 255: " << t.get() << std::endl;
    
    for (int i = 0; i < 1000; i++) {
        t += 255;
    }
    std::cout << "After 1000+ operations: " << t.get() << " (max=" << TRAIL_MAX << ")" << std::endl;
    
    return 0;
}
