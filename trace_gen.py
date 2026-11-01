import sys

def loop_gemm(m: int, n:int, p: int, arq_name = "trace_gemm") -> None:
    """
    Simula os acessos de memória relizados pelo algortimo 
    de General Matrix Multiply (MATRIX DENSA) e gera o arquivo trace.
    
    Começando da posição 0.
    A(mxn) começa em 0
    B(nxp) começa em m*n*4
    C(mxp) começa em 4*(mn + mp)
    """
    arq_result = open(f"tests/{arq_name}.in", "w")

    a_base = 0
    b_base = m*n*4
    c_base = 4*m*n + 4*n*p
    for i in range(m):
        for j in range(p):
            for k in range(n):                
                #acesso Aik
                pos_a = a_base + 4*m*i + 4*k
                print(pos_a, file=arq_result)
                #acesso Bkj
                pos_b = b_base + 4*n*k + 4*j
                print(pos_b, file=arq_result)
                #acesso Cij
                pos_c = c_base + 4*m*i + 4*j
                print(pos_c, file=arq_result)

    arq_result.close()

def loop_gemm_transposta(m: int, n: int, p: int, arq_name="trace_gemm_transposta") -> None:
    """
    Simula os acessos de memória do GEMM utilizando a matriz B previamente transposta.
    A(m x n) começa em 0
    B_T(p x n) começa em m*n*4
    C(m x p) começa a partir do fim de B_T
    """
    arq_result = open(f"tests/{arq_name}.in", "w")

    a_base = 0
    bt_base = m * n * 4
    c_base = bt_base + (p * n * 4)

    for i in range(m):
        for j in range(p):
            for k in range(n):                
                # Acesso Aik (contíguo na memória)
                pos_a = a_base + (i * n + k) * 4
                print(pos_a, file=arq_result)
                
                # Acesso B_T_jk (agora também é contíguo na memória)
                pos_b_trans = bt_base + (j * n + k) * 4
                print(pos_b_trans, file=arq_result)
                
                # Acesso Cij (fixo durante a execução do laço mais interno)
                pos_c = c_base + (i * p + j) * 4
                print(pos_c, file=arq_result)

    arq_result.close()
                    

def main():
    if sys.argv[1] == '-g':
        if len(sys.argv) < 5:
            raise ValueError("It lacks arguments in sys.argv")

        if len(sys.argv) == 5:
            loop_gemm(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))

        else:
            try:
                loop_gemm(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
            except (TypeError, ValueError):
                raise ValueError("You may have mixed the arguments in argv. Be cautios.")

    elif sys.argv[1] == '-gt':
            if len(sys.argv) == 5:
                loop_gemm_transposta(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
            else:
                try:
                    loop_gemm_transposta(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
                except (TypeError, ValueError):
                    raise ValueError("Argumentos inválidos no sys.argv.")
if __name__ == '__main__':
    main()