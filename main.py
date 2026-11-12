from mem_sim import MemorySimulator

test_path = "tests/trace.in"

mem_simulator = MemorySimulator(page_size=4096, num_tlb_entries=16, num_frames=64, rep_policy='Optimal', va_bits=32, access_trace= test_path)


arq_test = open(test_path, "r")

for addr in arq_test:
    mem_simulator.access_memory(int(addr))
mem_simulator.print_statistics()
arq_test.close()