import collections
import math

class MemorySimulator:
    def __init__(self, page_size, num_tlb_entries, num_frames, rep_policy, va_bits, access_trace = None):
        self.page_size = page_size
        self.num_tlb_entries = num_tlb_entries
        self.num_frames = num_frames    
        self.rep_policy = rep_policy
        self.va_bits = va_bits

        if rep_policy not in ['LRU', 'SecondChance', 'Optimal']:
            raise ValueError("Política de substituição inválida.")

        if rep_policy == 'Optimal' and access_trace is None:
            raise ValueError("Optimal requer um arquivo de trace.")

        self.rep_func = {
            'LRU': self._lru,
            'SecondChance': self._second_chance,
            'Optimal': self._optimal
        }[rep_policy]


        self.tlb = collections.OrderedDict()
        self.page_table = {} 
        self.frames = [None] * num_frames

        # contadores de estatísticas
        self.tlb_hits = 0
        self.tlb_misses = 0
        self.page_faults = 0

        #lru-variables
        self._lru_time_table: list = [math.inf] * num_frames
        self._lru_counting = 0

        #sc-variables
        self.clock_pointer = 0
        self.reference_bits = [0] * num_frames

        # optimal variables
        if access_trace is not None:
            with open(access_trace, 'r') as f:
                self.access_trace = [
                    int(line.strip()) >> int(math.log2(page_size))
                    for line in f if line.strip()
                ]
        else:
            self.access_trace = []

        self.trace_pointer = -1
        self.future_positions = collections.defaultdict(collections.deque)

        if rep_policy == 'Optimal':
            for i, page in enumerate(self.access_trace):
                self.future_positions[page].append(i)


    def _optimal(self) -> int:
        """
        Seleciona o frame cuja página será utilizada mais distante no futuro.
        Caso a página não volte a ser utilizada, seleciona-a imediatamente.
        """
        farthest = -1
        victim = -1

        for i, page in enumerate(self.frames):
            if not self.future_positions[page]:
                return i

            next_use = self.future_positions[page][0]

            if next_use > farthest:
                farthest = next_use
                victim = i

        return victim

    def _second_chance_update(self, frame_number: int) -> None:
        self.reference_bits[frame_number] = 1

    def _second_chance(self) -> int:
        while True:
            # Se o bit for 0, vítima
            if self.reference_bits[self.clock_pointer] == 0:
                victim = self.clock_pointer
                self.clock_pointer = (self.clock_pointer + 1) % self.num_frames
                return victim
            
            # Se for 1, zera (segunda chance) e avança o ponteiro
            self.reference_bits[self.clock_pointer] = 0
            self.clock_pointer = (self.clock_pointer + 1) % self.num_frames

    def _lru_update(self, frame_number:int) -> None:
        self._lru_counting += 1
        self._lru_time_table[frame_number] = self._lru_counting

    def _lru(self) -> int:
        """
        Encontra o frame_position a ser substituido. Aplicando a política de substituição
        Least-Recently-Updated (LRU).
        """
        max = 0
        for i, time in  enumerate(self._lru_time_table):
            if time < self._lru_time_table[max]:
                max = i

        return max

    def _update_tlb(self, page_number, frame_buffer):
        """
        Atualiza a tbl alocando o page->frame_buffer no espaço vazio ou liberando espaço pra uma nova entrada
        Replacement_Policy: LRU
        """
        self.tlb[page_number] = frame_buffer
        if len(self.tlb) > self.num_tlb_entries:
            # last=False remove no modelo FIFO (o primeiro que entrou/menos recente)
            self.tlb.popitem(last=False)

    def _alocate_frame(self, page_number: int) -> int:
        """
        Acha uma posição vazia para alocar a página. Caso não tenha,
        aplica uma política de substituição.

        Retorna: retorna o frame_number onde foi alocado.
        """
        for i, frame in enumerate(self.frames):
            if frame is None:
                self.frames[i] = page_number
                return i

        #apply replacement_policy
        replace_pos = self.rep_func()
        old_page = self.frames[replace_pos]

        #revome página vítima
        if old_page in self.page_table:
            del self.page_table[old_page]

            if old_page in self.tlb:
                del self.tlb[old_page]

        self.frames[replace_pos] = page_number
        return replace_pos
        

    def access_memory(self, virtual_address):
        """
        Simula o acesso a um endereço virtual.
        Deve atualizar os contadores e aplicar a política de substituição se necessário.
        """
        offset_bits = int(math.log2(self.page_size))
        page_number = virtual_address >> offset_bits

        if self.rep_policy == 'Optimal':
            self.trace_pointer += 1
            self.future_positions[page_number].popleft()

        if page_number in self.tlb:
            #tlb_hit
            self.tlb_hits += 1

            #marca como mais recente.
            self.tlb.move_to_end(page_number)

            frame_pos = self.tlb[page_number]

            #atualizando o contador para politica
            if self.rep_policy == 'LRU':
                self._lru_update(frame_pos)
            elif self.rep_policy == 'SecondChance':
                self._second_chance_update(frame_pos)

        else: #tlb miss
            self.tlb_misses += 1

            #verificar page_table
            if self.page_table.get(page_number) is None: #page_fault
                self.page_faults += 1
                #aloco na memória física.
                new_frame_pos = self._alocate_frame(page_number)
                self.page_table[page_number] = new_frame_pos
                
            else:
                new_frame_pos = self.page_table[page_number]

            #atulizando contadores da rep_policy
            if self.rep_policy == 'LRU':
                self._lru_update(new_frame_pos)
            elif self.rep_policy == 'SecondChance':
                self._second_chance_update(new_frame_pos)

            self._update_tlb(page_number, new_frame_pos)

        
    def print_statistics(self):
        print("=" * 60)
        print("SIMULADOR DE MEMÓRIA - Estatísticas de Acesso")
        print("=" * 60)
        print(f"Política de Substituição:   {self.rep_policy}")
        print(f"Tamanho da Página:          {self.page_size} bytes")
        print(f"Entradas na TLB:            {self.num_tlb_entries}")
        print(f"Número de Frames:           {self.num_frames}")
        print("-" * 60)
        print(f"TLB Hits:                   {self.tlb_hits:,}")
        print(f"TLB Misses:                 {self.tlb_misses:,}")
        print(f"Page Faults:                {self.page_faults:,}")
        print("=" * 60)