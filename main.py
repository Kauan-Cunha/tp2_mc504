from mem_sim import MemorySimulator

mem_simulator = MemorySimulator(page_size=4096, num_tlb_entries=16, num_frames=64, rep_policy='LRU', va_bits=32)


arq_test = open("tests/trace.in", "r")

for addr in arq_test:
    mem_simulator.access_memory(int(addr))
mem_simulator.print_statistics()

