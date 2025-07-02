import os
import re
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
    Document,
    load_index_from_storage
)
from llama_index.llms.groq import Groq
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Diretórios usados
PERSIST_DIR = "backend/index"
UPLOADS_DIR = "backend/data/uploads"

# Variáveis globais
_index = None
_initialized = False

# PROMPT EDUCACIONAL OTIMIZADO - DETALHADO MAS CONCISO
OPTIMIZED_EDUCATIONAL_PROMPT = """
VOCÊ É O PENSA.AI - TUTOR EDUCACIONAL ESPECIALISTA

MISSÃO: Ensinar detalhadamente com exemplos passo a passo, mas SEM dar o resultado final.

ESTRUTURA OBRIGATÓRIA:

🎯 ANÁLISE: [Tipo de problema e conceitos envolvidos]

📚 CONCEITOS: [Definições claras e aplicações]

📐 FÓRMULAS: [Todas as fórmulas necessárias com explicação das variáveis]

🛠️ MÉTODO PASSO A PASSO:
Passo 1: [O que fazer e como]
Passo 2: [Próxima etapa]
[Continue conforme necessário]

📝 EXEMPLO RESOLVIDO:
Problema: [Similar mas diferente]
Resolução:
- Dados: [o que temos]
- Aplicação: [como resolver]
- Cálculos: [passo a passo]
- Resultado: [resposta do exemplo]

📝 SEGUNDO EXEMPLO:
[Outro exemplo com resolução completa]

🔄 VERIFICAÇÃO: [Como conferir os resultados]

🎯 PARA SEU PROBLEMA: [Orientação específica SEM resolver]

IMPORTANTE: Dê exemplos COMPLETOS com resultado final, mas NÃO resolva o problema específico perguntado.
"""

def setup_embedding_model():
    """Configura modelo de embedding local"""
    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        
        embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder="./embeddings_cache"
        )
        
        Settings.embed_model = embed_model
        print("✅ Embedding local configurado!")
        return True
        
    except ImportError:
        print("⚠️ Usando embedding padrão")
        return True
    except Exception as e:
        print(f"⚠️ Erro no embedding: {e}")
        return True

def setup_llama_index():
    """Configura LlamaIndex otimizado"""
    global _initialized
    
    if _initialized:
        return True
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY não encontrada no arquivo .env")
        return False
    
    try:
        setup_embedding_model()
        
        # Configurações OTIMIZADAS para evitar erro de contexto
        llm = Groq(
            model="llama3-8b-8192",  # Modelo mais estável
            api_key=groq_api_key,
            temperature=0.2,
            max_tokens=2048,  # Limite seguro de tokens
            timeout=30,
        )
        
        Settings.llm = llm
        
        # Configurações do índice para respostas mais concisas
        Settings.chunk_size = 512  # Chunks menores
        Settings.chunk_overlap = 50
        
        # Teste de conectividade
        print("🧪 Testando Groq...")
        test_response = llm.complete("Teste rápido")
        print("✅ Groq funcionando!")
        
        _initialized = True
        print("✅ Sistema educacional OTIMIZADO configurado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar: {str(e)}")
        return False

def ensure_directories():
    """Garante diretórios necessários"""
    try:
        directories = [UPLOADS_DIR, PERSIST_DIR, "./embeddings_cache"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Erro ao criar diretórios: {str(e)}")
        return False

def create_optimized_educational_index():
    """Cria índice educacional otimizado"""
    try:
        educational_content = Document(
            text="""
            PENSA.AI - SISTEMA EDUCACIONAL OTIMIZADO
            
            MATEMÁTICA - Guia Conciso:
            
            ÁLGEBRA:
            • Equação linear ax + b = c: isole x dividindo por a
            • Equação quadrática ax² + bx + c = 0: use Bhaskara x = (-b ± √Δ)/2a
            • Δ = b² - 4ac determina número de soluções
            
            GEOMETRIA:
            • Área retângulo: A = base × altura
            • Área triângulo: A = (base × altura)/2  
            • Área círculo: A = πr²
            • Pitágoras: a² + b² = c²
            
            FUNÇÕES:
            • Linear f(x) = ax + b: reta com inclinação a
            • Quadrática f(x) = ax² + bx + c: parábola
            • Vértice: x = -b/2a
            
            FÍSICA - Conceitos Base:
            
            CINEMÁTICA:
            • MRU: s = s₀ + vt
            • MRUV: v = v₀ + at, s = s₀ + v₀t + at²/2
            
            DINÂMICA:
            • F = ma (2ª Lei Newton)
            • Peso: P = mg
            
            QUÍMICA - Essencial:
            
            ESTEQUIOMETRIA:
            • Mol = 6,02×10²³ partículas
            • n = m/M (mols = massa/massa molar)
            
            METODOLOGIA:
            1. Identifique o problema
            2. Liste dados e incógnitas
            3. Escolha fórmulas adequadas
            4. Resolva passo a passo
            5. Verifique o resultado
            """
        )
        
        index = VectorStoreIndex.from_documents([educational_content])
        print("✅ Índice educacional otimizado criado")
        return index
        
    except Exception as e:
        print(f"❌ Erro ao criar índice: {str(e)}")
        return None

def build_index_from_documents():
    """Constrói índice otimizado"""
    try:
        ensure_directories()
        
        documents = []
        
        # Carregar PDFs educacionais
        if os.path.exists(UPLOADS_DIR):
            pdf_files = [f for f in os.listdir(UPLOADS_DIR) if f.lower().endswith('.pdf')]
            
            if pdf_files:
                print(f"📖 Processando {len(pdf_files)} materiais...")
                try:
                    loaded_docs = SimpleDirectoryReader(UPLOADS_DIR).load_data()
                    for doc in loaded_docs:
                        # Texto mais conciso para evitar overflow
                        enhanced_text = f"""
MATERIAL EDUCACIONAL:

CONTEÚDO:
{doc.text[:2000]}  

INSTRUÇÕES:
- Ensine conceitos detalhadamente
- Dê fórmulas completas
- Resolva exemplos similares
- Oriente aplicação sem dar resultado final
                        """
                        enhanced_doc = Document(text=enhanced_text)
                        documents.append(enhanced_doc)
                        
                except Exception as e:
                    print(f"⚠️ Erro ao processar PDFs: {e}")
        
        # Base educacional
        base_index = create_optimized_educational_index()
        if base_index:
            base_docs = list(base_index.docstore.docs.values())
            documents.extend(base_docs)
        
        if not documents:
            return create_optimized_educational_index()
        
        # Criar índice
        index = VectorStoreIndex.from_documents(documents)
        
        # Salvar índice
        try:
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            print("💾 Índice otimizado salvo")
        except Exception as e:
            print(f"⚠️ Erro ao salvar: {e}")
        
        print(f"✅ Base educacional otimizada com {len(documents)} recursos")
        return index
        
    except Exception as e:
        print(f"❌ Erro ao construir base: {str(e)}")
        return create_optimized_educational_index()

def get_index():
    """Retorna índice educacional"""
    global _index
    
    if _index is not None:
        return _index
    
    try:
        # Tentar carregar índice existente
        if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
            print("📚 Carregando base educacional...")
            try:
                storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
                _index = load_index_from_storage(storage_context)
                print("✅ Base carregada!")
                return _index
            except Exception as e:
                print(f"⚠️ Erro ao carregar: {e}")
                print("🔄 Criando nova base...")
                # Limpar índice incompatível
                try:
                    import shutil
                    shutil.rmtree(PERSIST_DIR)
                    ensure_directories()
                except:
                    pass
        
        # Criar nova base
        print("🆕 Criando base educacional otimizada...")
        _index = build_index_from_documents()
        return _index
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        _index = create_optimized_educational_index()
        return _index

def is_educational_query(query: str) -> bool:
    """Verificação para perguntas educacionais"""
    non_educational = [
        'clima hoje', 'temperatura agora', 'notícias atuais',
        'que horas são', 'data de hoje'
    ]
    
    query_lower = query.lower()
    return not any(term in query_lower for term in non_educational)

def generate_detailed_response(query: str) -> str:
    """Gera resposta detalhada de forma estruturada"""
    
    # Identifica tipo de problema
    if any(word in query.lower() for word in ['função', 'gráfico', 'parábola', 'reta']):
        return generate_function_response(query)
    elif any(word in query.lower() for word in ['equação', 'resolver', 'x=']):
        return generate_equation_response(query)
    elif any(word in query.lower() for word in ['área', 'perímetro', 'volume']):
        return generate_geometry_response(query)
    else:
        return generate_general_response(query)

def generate_function_response(query: str) -> str:
    """Resposta específica para funções"""
    return f"""
🎯 ANÁLISE DO PROBLEMA: {query}

Este é um problema de FUNÇÃO que envolve análise gráfica e cálculo de retas.

📚 CONCEITOS FUNDAMENTAIS:
• Função Quadrática: f(x) = ax² + bx + c (parábola)
• Reta Secante: liga dois pontos da curva
• Coeficiente Angular: m = (y₂-y₁)/(x₂-x₁)

📐 FÓRMULAS NECESSÁRIAS:
• Vértice da parábola: x = -b/2a
• Equação da reta: y - y₁ = m(x - x₁)
• Ponto da função: y = f(x)

🛠️ MÉTODO PASSO A PASSO:
Passo 1: Verifique se o ponto pertence à função
Passo 2: Calcule outros pontos da função
Passo 3: Desenhe o gráfico da função
Passo 4: Escolha pontos para as secantes
Passo 5: Calcule coeficientes angulares
Passo 6: Encontre equações das retas
Passo 7: Desenhe as retas secantes

📝 EXEMPLO RESOLVIDO:
Problema: f(x) = x² - 2x, ponto A(1,-1)

Verificação: f(1) = 1² - 2(1) = 1 - 2 = -1 ✓

Outros pontos:
• f(0) = 0 - 0 = 0 → (0,0)
• f(2) = 4 - 4 = 0 → (2,0)  
• f(3) = 9 - 6 = 3 → (3,3)

Reta secante A(1,-1) e B(3,3):
• m = (3-(-1))/(3-1) = 4/2 = 2
• y - (-1) = 2(x - 1)
• y = 2x - 3

📝 SEGUNDO EXEMPLO:
Função g(x) = -x² + 4x, ponto C(1,3)

Verificação: g(1) = -1 + 4 = 3 ✓

Reta secante C(1,3) e D(2,4):
• g(2) = -4 + 8 = 4
• m = (4-3)/(2-1) = 1
• y = x + 2

🔄 VERIFICAÇÃO:
• Substitua pontos nas equações das retas
• Confira que passam pelos pontos corretos
• Desenhe para verificar visualmente

🎯 PARA SEU PROBLEMA:
1. Verifique se o ponto dado pertence à função
2. Calcule valores da função para outros x
3. Escolha pontos para as secantes
4. Use m = (y₂-y₁)/(x₂-x₁) para cada reta
5. Encontre as equações na forma y = mx + b
6. Desenhe tudo no mesmo gráfico

Agora você tem o método completo para resolver!
    """

def generate_equation_response(query: str) -> str:
    """Resposta específica para equações"""
    return f"""
🎯 ANÁLISE DO PROBLEMA: {query}

Este é um problema de EQUAÇÃO que requer técnicas algébricas.

📚 CONCEITOS FUNDAMENTAIS:
• Equação: igualdade com incógnita
• Solução: valor que satisfaz a equação
• Operações inversas: +/-, ×/÷, potência/raiz

📐 FÓRMULAS NECESSÁRIAS:
• Linear: ax + b = c → x = (c-b)/a
• Quadrática: ax² + bx + c = 0 → x = (-b ± √Δ)/2a
• Δ = b² - 4ac (discriminante)

🛠️ MÉTODO PASSO A PASSO:
Passo 1: Identifique o tipo de equação
Passo 2: Organize termos (x de um lado)
Passo 3: Aplique operações inversas
Passo 4: Calcule o resultado
Passo 5: Verifique substituindo

📝 EXEMPLO RESOLVIDO:
Problema: 3x + 7 = 22

Resolução:
• 3x = 22 - 7
• 3x = 15
• x = 15/3
• x = 5

Verificação: 3(5) + 7 = 15 + 7 = 22 ✓

📝 SEGUNDO EXEMPLO:
Problema: x² - 5x + 6 = 0

Resolução:
• a = 1, b = -5, c = 6
• Δ = (-5)² - 4(1)(6) = 25 - 24 = 1
• x = (5 ± √1)/2 = (5 ± 1)/2
• x₁ = 6/2 = 3, x₂ = 4/2 = 2

Verificação: 3² - 5(3) + 6 = 9 - 15 + 6 = 0 ✓

🔄 VERIFICAÇÃO:
• Substitua a solução na equação original
• O resultado deve ser verdadeiro
• Para quadráticas, teste ambas as raízes

🎯 PARA SEU PROBLEMA:
1. Identifique se é linear ou quadrática
2. Organize os termos adequadamente
3. Aplique a fórmula correspondente
4. Execute os cálculos passo a passo
5. Sempre verifique o resultado

Use este método para resolver sua equação!
    """

def generate_geometry_response(query: str) -> str:
    """Resposta específica para geometria"""
    return f"""
🎯 ANÁLISE DO PROBLEMA: {query}

Este é um problema de GEOMETRIA que envolve cálculos de medidas.

📚 CONCEITOS FUNDAMENTAIS:
• Área: medida da superfície (unidade²)
• Perímetro: medida do contorno (unidade)
• Volume: medida do espaço (unidade³)

📐 FÓRMULAS NECESSÁRIAS:
• Retângulo: A = b×h, P = 2(b+h)
• Triângulo: A = (b×h)/2, P = a+b+c
• Círculo: A = πr², P = 2πr
• Cubo: V = a³, A = 6a²

🛠️ MÉTODO PASSO A PASSO:
Passo 1: Identifique a figura geométrica
Passo 2: Liste as medidas conhecidas
Passo 3: Escolha a fórmula adequada
Passo 4: Substitua os valores
Passo 5: Calcule o resultado com unidades

📝 EXEMPLO RESOLVIDO:
Problema: Área de um retângulo 8cm × 5cm

Resolução:
• Base = 8cm, Altura = 5cm
• A = base × altura
• A = 8 × 5 = 40 cm²

📝 SEGUNDO EXEMPLO:
Problema: Área de círculo com raio 3cm

Resolução:
• r = 3cm
• A = πr²
• A = π × 3² = 9π ≈ 28,3 cm²

🔄 VERIFICAÇÃO:
• Confira as unidades (área em unidade²)
• Verifique se o resultado é razoável
• Refaça com fórmula alternativa se possível

🎯 PARA SEU PROBLEMA:
1. Identifique que medida calcular
2. Reconheça a figura geométrica
3. Use a fórmula correspondente
4. Substitua valores com cuidado
5. Inclua unidades no resultado

Aplique este método na sua questão!
    """

def generate_general_response(query: str) -> str:
    """Resposta geral estruturada"""
    return f"""
🎯 ANÁLISE DO PROBLEMA: {query}

Vou ensinar o método geral para resolver este tipo de problema.

📚 CONCEITOS FUNDAMENTAIS:
Identifique os conceitos envolvidos na sua questão para aplicar a teoria correta.

📐 FÓRMULAS NECESSÁRIAS:
Determine quais fórmulas e métodos são adequados para seu problema específico.

🛠️ MÉTODO PASSO A PASSO:
Passo 1: Leia e compreenda completamente
Passo 2: Identifique dados e incógnitas
Passo 3: Escolha estratégia adequada
Passo 4: Execute sistematicamente
Passo 5: Verifique o resultado

📝 EXEMPLO GERAL:
Para qualquer problema educacional:
• Organize informações claramente
• Aplique conceitos fundamentais
• Use fórmulas adequadas
• Calcule passo a passo
• Confira o resultado

🔄 VERIFICAÇÃO:
• Substitua resultado no problema original
• Analise se faz sentido prático
• Use método alternativo se possível

🎯 PARA SEU PROBLEMA:
Aplique esta metodologia sistemática na sua questão específica, seguindo cada etapa cuidadosamente.
    """

def get_response_from_query(query: str) -> str:
    """Gera resposta educacional otimizada"""
    try:
        print(f"🎓 Processando pergunta: {query[:50]}...")
        
        # Verificação educacional
        if not is_educational_query(query):
            return """
🎓 Como tutor educacional, foco em questões de aprendizado!

📚 POSSO ENSINAR:
• Matemática: álgebra, geometria, funções
• Física: cinemática, dinâmica, energia
• Química: estequiometria, soluções
• Métodos de resolução detalhados

🤔 Reformule para uma pergunta educacional!
            """
        
        # Verificar sistema
        if not setup_llama_index():
            return generate_detailed_response(query)
        
        # Obter base de conhecimento
        index = get_index()
        if index is None:
            return generate_detailed_response(query)
        
        # Configurar query engine OTIMIZADO
        query_engine = index.as_query_engine(
            similarity_top_k=2,  # Menos contexto para evitar overflow
            response_mode="compact",  # Modo mais conciso
            streaming=False
        )
        
        # Prompt otimizado e mais curto
        optimized_prompt = f"""
{OPTIMIZED_EDUCATIONAL_PROMPT}

PERGUNTA: {query}

Dê uma resposta educacional detalhada mas concisa, com exemplos resolvidos.
        """
        
        print("🔄 Gerando resposta educacional...")
        
        try:
            response = query_engine.query(optimized_prompt)
            result = str(response)
            
            # Se resposta muito curta, usar fallback
            if len(result) < 200:
                result = generate_detailed_response(query)
            
            print("✅ Resposta educacional gerada")
            return result
            
        except Exception as e:
            print(f"❌ Erro na consulta: {e}")
            return generate_detailed_response(query)
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return generate_detailed_response(query)

def update_index():
    """Atualiza base educacional"""
    global _index
    
    try:
        print("🔄 Atualizando base educacional...")
        
        if not setup_llama_index():
            return False
        
        _index = None
        _index = build_index_from_documents()
        
        success = _index is not None
        print(f"{'✅' if success else '❌'} Base {'atualizada' if success else 'falhou'}")
        return success
        
    except Exception as e:
        print(f"❌ Erro ao atualizar: {str(e)}")
        return False

# Inicialização otimizada
print("🎓 Inicializando Pensa.AI - SISTEMA OTIMIZADO...")
print("📋 CARACTERÍSTICAS:")
print("   ✅ Respostas detalhadas e estruturadas")
print("   ✅ Exemplos resolvidos passo a passo")
print("   ✅ Múltiplas estratégias de ensino")
print("   ✅ Otimizado para evitar erros de contexto")
print("   ❌ NÃO dá resultado final do problema específico")

try:
    if setup_llama_index():
        ensure_directories()
        get_index()
        print("✅ Sistema EDUCACIONAL OTIMIZADO pronto!")
    else:
        print("⚠️ Sistema com limitações - verifique GROQ_API_KEY")
except Exception as e:
    print(f"❌ Erro na inicialização: {e}")
    