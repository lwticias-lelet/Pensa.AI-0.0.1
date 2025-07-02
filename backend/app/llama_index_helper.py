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

# SISTEMA DE PROMPTS EDUCACIONAIS ULTRA DETALHADO
ULTRA_DETAILED_EDUCATIONAL_PROMPT = """
VOCÊ É O PENSA.AI - TUTOR EDUCACIONAL ESPECIALISTA ULTRA DETALHADO

MISSÃO: Ensinar de forma EXTREMAMENTE DETALHADA com exemplos PASSO A PASSO COMPLETOS

REGRAS OBRIGATÓRIAS:
✅ SEMPRE forneça explicações MUITO detalhadas
✅ SEMPRE dê exemplos COMPLETOS resolvidos passo a passo
✅ SEMPRE explique CADA etapa minuciosamente
✅ SEMPRE conecte teoria com prática
✅ SEMPRE use múltiplos exemplos quando necessário
❌ JAMAIS dê o resultado final do problema específico perguntado

ESTRUTURA OBRIGATÓRIA ULTRA DETALHADA:

🎯 ANÁLISE COMPLETA DO PROBLEMA:
[Analise detalhadamente que tipo de problema é, quais conceitos estão envolvidos, e o que precisa ser compreendido]

📚 CONCEITOS FUNDAMENTAIS DETALHADOS:
[Para CADA conceito necessário, forneça:]
• Definição completa e clara
• Importância e aplicações
• Relação com outros conceitos
• Propriedades principais
• Quando e como usar

📐 FÓRMULAS E MÉTODOS COMPLETOS:
[Para CADA fórmula:]
• Fórmula completa com explicação de CADA variável
• Quando usar esta fórmula
• Como aplicar passo a passo
• Variações da fórmula
• Cuidados e limitações

🛠️ MÉTODO DE RESOLUÇÃO ULTRA DETALHADO:
Passo 1: [Primeira etapa - O QUE fazer]
   💡 Como executar: [Instruções MUITO detalhadas]
   📋 Exemplo prático: [Demonstração com números]
   🔍 O que observar: [Pontos de atenção]
   ⚠️ Erros comuns: [O que evitar]

Passo 2: [Segunda etapa - O QUE fazer]
   💡 Como executar: [Instruções MUITO detalhadas]
   📋 Exemplo prático: [Demonstração com números]
   🔍 O que observar: [Pontos de atenção]
   ⚠️ Erros comuns: [O que evitar]

[Continue para TODOS os passos necessários]

📝 EXEMPLO COMPLETO RESOLVIDO PASSO A PASSO:
Problema exemplo: [Enunciado SIMILAR mas DIFERENTE do perguntado]

Resolução DETALHADA:
Passo 1: Identificação e Análise
- O que temos: [Liste TODOS os dados]
- O que procuramos: [Especifique claramente]
- Estratégia: [Explique como abordar]

Passo 2: Aplicação dos Conceitos
- Conceito aplicado: [Qual e por quê]
- Fórmula escolhida: [Qual e justificativa]
- Substituição: [Mostre número por número]

Passo 3: Cálculos Detalhados
- Operação 1: [Mostre cada conta]
- Operação 2: [Mostre cada conta]
- Resultado parcial: [Explique o que significa]

Passo 4: Verificação e Interpretação
- Verificação: [Como conferir se está certo]
- Interpretação: [O que o resultado significa]
- Resposta final: [Resultado COMPLETO do exemplo]

📝 SEGUNDO EXEMPLO DETALHADO:
[Outro problema similar com resolução completa para reforçar o aprendizado]

📝 TERCEIRO EXEMPLO (SE NECESSÁRIO):
[Caso o tópico seja complexo, forneça mais exemplos]

🔄 MÉTODOS DE VERIFICAÇÃO DETALHADOS:
• Método 1: [Como verificar - passo a passo]
• Método 2: [Forma alternativa de conferir]
• Sinais de erro: [Como identificar problemas]
• Conferência final: [Checklist completo]

🎯 APLICAÇÃO NO SEU PROBLEMA ESPECÍFICO:
[Orientações MUITO detalhadas para o problema perguntado SEM resolvê-lo]

Para resolver SEU problema específico, siga estes passos:

Etapa 1: Análise Inicial
- Identifique: [O que procurar especificamente]
- Organize: [Como estruturar os dados]
- Planeje: [Estratégia recomendada]

Etapa 2: Aplicação dos Conceitos
- Use o conceito: [Qual aplicar e como]
- Aplique a fórmula: [Como fazer a substituição]
- Execute os cálculos: [Sequência de operações]

Etapa 3: Verificação
- Confira usando: [Métodos de verificação]
- Interprete: [Como entender o resultado]

🤔 PERGUNTAS PARA REFLEXÃO:
• [Pergunta 1 para consolidar o aprendizado]
• [Pergunta 2 para conexão com outros tópicos]
• [Pergunta 3 para aplicação prática]

🔗 CONEXÕES COM OUTROS TÓPICOS:
[Como este assunto se relaciona com outros conceitos]

💡 DICAS IMPORTANTES:
• [Dica 1 para melhor compreensão]
• [Dica 2 para evitar erros]
• [Dica 3 para aplicação eficiente]

LEMBRE-SE: Ensine TUDO com MÁXIMO DETALHAMENTO, mas deixe o estudante resolver o problema específico!
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
    """Configura LlamaIndex para ensino ULTRA detalhado"""
    global _initialized
    
    if _initialized:
        return True
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY não encontrada no arquivo .env")
        return False
    
    try:
        setup_embedding_model()
        
        # Configurações otimizadas para respostas MUITO detalhadas
        llm = Groq(
            model="llama3-70b-8192",  # Modelo maior para respostas mais detalhadas
            api_key=groq_api_key,
            temperature=0.1,  # Baixa para precisão
            max_tokens=4000,  # Máximo para respostas longas e detalhadas
            timeout=45,
        )
        
        Settings.llm = llm
        
        # Teste de conectividade
        print("🧪 Testando Groq com modelo maior...")
        test_response = llm.complete("Teste de conectividade detalhado")
        print("✅ Groq funcionando com modelo avançado!")
        
        _initialized = True
        print("✅ Sistema educacional ULTRA DETALHADO configurado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar: {str(e)}")
        # Fallback para modelo menor se o maior falhar
        try:
            llm = Groq(
                model="llama3-8b-8192",
                api_key=groq_api_key,
                temperature=0.1,
                max_tokens=3000,
                timeout=35,
            )
            Settings.llm = llm
            _initialized = True
            print("✅ Sistema configurado com modelo alternativo!")
            return True
        except Exception as e2:
            print(f"❌ Erro completo: {str(e2)}")
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

def create_enhanced_educational_index():
    """Cria índice com conhecimento educacional ULTRA completo"""
    try:
        educational_content = Document(
            text="""
            PENSA.AI - SISTEMA EDUCACIONAL ULTRA DETALHADO
            
            METODOLOGIA DE ENSINO COMPLETA:
            
            MATEMÁTICA - Conceitos e Aplicações Detalhadas:
            
            ÁLGEBRA COMPLETA:
            
            Equações do Primeiro Grau:
            • Definição: Equação da forma ax + b = c, onde a ≠ 0
            • Método de resolução:
              1. Isolar termos com x de um lado
              2. Isolar termos constantes do outro lado
              3. Dividir ambos os membros pelo coeficiente de x
            • Exemplo detalhado: 3x + 7 = 22
              - Passo 1: 3x = 22 - 7
              - Passo 2: 3x = 15
              - Passo 3: x = 15/3 = 5
              - Verificação: 3(5) + 7 = 15 + 7 = 22 ✓
            
            Equações do Segundo Grau:
            • Definição: Equação da forma ax² + bx + c = 0, onde a ≠ 0
            • Fórmula de Bhaskara: x = (-b ± √(b²-4ac))/2a
            • Discriminante: Δ = b² - 4ac
            • Interpretação do discriminante:
              - Δ > 0: duas raízes reais distintas
              - Δ = 0: uma raiz real (raiz dupla)
              - Δ < 0: não há raízes reais
            • Exemplo completo: x² - 5x + 6 = 0
              - Identificação: a = 1, b = -5, c = 6
              - Cálculo do discriminante: Δ = (-5)² - 4(1)(6) = 25 - 24 = 1
              - Aplicação da fórmula: x = (5 ± √1)/2 = (5 ± 1)/2
              - Raízes: x₁ = 6/2 = 3 e x₂ = 4/2 = 2
              - Verificação: (3)² - 5(3) + 6 = 9 - 15 + 6 = 0 ✓
            
            GEOMETRIA DETALHADA:
            
            Área e Perímetro:
            • Retângulo:
              - Área: A = base × altura
              - Perímetro: P = 2(base + altura)
              - Exemplo: base = 8cm, altura = 5cm
                * Área: A = 8 × 5 = 40 cm²
                * Perímetro: P = 2(8 + 5) = 2(13) = 26 cm
            
            • Triângulo:
              - Área: A = (base × altura)/2
              - Perímetro: P = lado₁ + lado₂ + lado₃
              - Exemplo: base = 10cm, altura = 6cm
                * Área: A = (10 × 6)/2 = 60/2 = 30 cm²
            
            • Círculo:
              - Área: A = πr²
              - Perímetro (circunferência): C = 2πr
              - Exemplo: raio = 4cm
                * Área: A = π(4)² = 16π ≈ 50,27 cm²
                * Circunferência: C = 2π(4) = 8π ≈ 25,13 cm
            
            Teorema de Pitágoras:
            • Enunciado: Em um triângulo retângulo, o quadrado da hipotenusa é igual à soma dos quadrados dos catetos
            • Fórmula: a² + b² = c², onde c é a hipotenusa
            • Exemplo detalhado: catetos de 3cm e 4cm
              - Aplicação: 3² + 4² = c²
              - Cálculo: 9 + 16 = c²
              - Resultado: c² = 25, logo c = 5cm
              - Verificação: √(3² + 4²) = √(9 + 16) = √25 = 5 ✓
            
            FUNÇÕES MATEMÁTICAS:
            
            Função Linear: f(x) = ax + b
            • Coeficiente angular (a): determina a inclinação da reta
            • Coeficiente linear (b): ponto onde a reta corta o eixo y
            • Exemplo: f(x) = 2x + 3
              - Para x = 0: f(0) = 2(0) + 3 = 3
              - Para x = 1: f(1) = 2(1) + 3 = 5
              - Para x = 2: f(2) = 2(2) + 3 = 7
            
            Função Quadrática: f(x) = ax² + bx + c
            • Vértice: V = (-b/2a, -Δ/4a)
            • Eixo de simetria: x = -b/2a
            • Exemplo: f(x) = x² - 4x + 3
              - Coeficientes: a = 1, b = -4, c = 3
              - Eixo de simetria: x = -(-4)/2(1) = 4/2 = 2
              - Vértice: V = (2, f(2)) = (2, 4 - 8 + 3) = (2, -1)
            
            FÍSICA - Conceitos Fundamentais:
            
            CINEMÁTICA:
            
            Movimento Retilíneo Uniforme (MRU):
            • Características: velocidade constante, aceleração zero
            • Equação: s = s₀ + vt
            • Exemplo detalhado: 
              - Posição inicial: s₀ = 5m
              - Velocidade: v = 10m/s
              - Tempo: t = 3s
              - Cálculo: s = 5 + 10(3) = 5 + 30 = 35m
            
            Movimento Retilíneo Uniformemente Variado (MRUV):
            • Características: aceleração constante
            • Equações:
              - v = v₀ + at
              - s = s₀ + v₀t + at²/2
              - v² = v₀² + 2aΔs
            • Exemplo completo:
              - Velocidade inicial: v₀ = 2m/s
              - Aceleração: a = 3m/s²
              - Tempo: t = 4s
              - Velocidade final: v = 2 + 3(4) = 2 + 12 = 14m/s
              - Deslocamento: s = 0 + 2(4) + 3(4)²/2 = 8 + 24 = 32m
            
            DINÂMICA:
            
            Leis de Newton:
            • 1ª Lei (Inércia): Todo corpo permanece em repouso ou em movimento retilíneo uniforme, a menos que seja obrigado a mudar por forças aplicadas
            • 2ª Lei (F = ma): A aceleração de um objeto é diretamente proporcional à força aplicada e inversamente proporcional à sua massa
            • 3ª Lei (Ação e Reação): Para toda ação há uma reação igual e oposta
            
            Exemplo de aplicação da 2ª Lei:
            • Força aplicada: F = 20N
            • Massa do objeto: m = 4kg
            • Aceleração: a = F/m = 20/4 = 5m/s²
            
            QUÍMICA - Fundamentos:
            
            ESTEQUIOMETRIA:
            • Conceito: Cálculo das quantidades das substâncias em reações químicas
            • Mol: 6,02 × 10²³ partículas (número de Avogadro)
            • Massa molar: massa de 1 mol da substância
            • Exemplo: H₂O
              - Massa molar: 2(1) + 16 = 18 g/mol
              - 2 mols de H₂O = 2 × 18 = 36g
            
            ESTRATÉGIAS PEDAGÓGICAS AVANÇADAS:
            1. Partir sempre do conceito fundamental
            2. Dar múltiplos exemplos com resolução completa
            3. Mostrar diferentes métodos de resolução
            4. Conectar teoria com aplicações práticas
            5. Ensinar métodos de verificação
            6. Estimular raciocínio crítico através de perguntas
            7. Fornecer dicas para evitar erros comuns
            8. Relacionar com conhecimentos anteriores
            """
        )
        
        index = VectorStoreIndex.from_documents([educational_content])
        print("✅ Índice educacional ULTRA detalhado criado")
        return index
        
    except Exception as e:
        print(f"❌ Erro ao criar índice: {str(e)}")
        return None

def build_index_from_documents():
    """Constrói índice educacional ULTRA completo"""
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
                        enhanced_text = f"""
MATERIAL EDUCACIONAL PARA ENSINO ULTRA DETALHADO:

CONTEÚDO ORIGINAL:
{doc.text}

INSTRUÇÕES PEDAGÓGICAS ULTRA DETALHADAS:

1. ENSINO EXTREMAMENTE COMPLETO:
- Explique TODOS os conceitos com máximo detalhamento
- Forneça definições completas e exemplos múltiplos
- Mostre aplicações práticas e importância
- Conecte com outros conhecimentos extensivamente

2. FÓRMULAS E MÉTODOS ULTRA DETALHADOS:
- Apresente TODAS as fórmulas com explicação de cada variável
- Mostre quando, como e por que usar cada fórmula
- Dê exemplos de aplicação para cada fórmula
- Ensine variações e casos especiais

3. RESOLUÇÃO PASSO A PASSO ULTRA COMPLETA:
- Ensine metodologia completa com muitos detalhes
- Mostre CADA etapa minuciosamente
- Explique o raciocínio completo por trás de cada passo
- Indique pontos de atenção e erros comuns detalhadamente

4. EXEMPLOS RESOLVIDOS ULTRA DETALHADOS:
- Resolva pelo menos 2-3 exemplos SIMILARES mas DIFERENTES da pergunta
- Mostre resolução COMPLETA com resultado final nos exemplos
- Varie tipos de problemas para fixar conceitos
- Explique estratégias e métodos alternativos

5. APLICAÇÃO GUIADA MUITO DETALHADA:
- Oriente minuciosamente como aplicar no problema específico
- Identifique dados e incógnitas detalhadamente
- Sugira estratégia de resolução passo a passo
- NÃO resolva completamente o problema perguntado

6. VERIFICAÇÃO E CONFERÊNCIA DETALHADA:
- Ensine múltiplos métodos de verificação
- Mostre como identificar e corrigir erros
- Dê dicas detalhadas de conferência de resultados
                        """
                        enhanced_doc = Document(text=enhanced_text)
                        documents.append(enhanced_doc)
                        
                except Exception as e:
                    print(f"⚠️ Erro ao processar PDFs: {e}")
        
        # Base educacional sempre presente
        base_content = create_enhanced_educational_index()
        if base_content:
            documents.extend(base_content.docstore.docs.values())
        
        if not documents:
            return create_enhanced_educational_index()
        
        # Criar índice
        index = VectorStoreIndex.from_documents(documents)
        
        # Salvar índice
        try:
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            print("💾 Índice educacional ULTRA detalhado salvo")
        except Exception as e:
            print(f"⚠️ Erro ao salvar: {e}")
        
        print(f"✅ Base educacional ULTRA completa com {len(documents)} recursos")
        return index
        
    except Exception as e:
        print(f"❌ Erro ao construir base: {str(e)}")
        return create_enhanced_educational_index()

def get_index():
    """Retorna índice educacional"""
    global _index
    
    if _index is not None:
        return _index
    
    try:
        # Tentar carregar índice existente
        if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
            print("📚 Carregando base educacional ULTRA detalhada...")
            try:
                storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
                _index = load_index_from_storage(storage_context)
                print("✅ Base ULTRA detalhada carregada!")
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
        print("🆕 Criando base educacional ULTRA detalhada...")
        _index = build_index_from_documents()
        return _index
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        _index = create_enhanced_educational_index()
        return _index

def is_educational_query(query: str) -> bool:
    """Verificação permissiva para perguntas educacionais"""
    non_educational = [
        'clima hoje', 'temperatura agora', 'notícias atuais',
        'que horas são', 'data de hoje'
    ]
    
    query_lower = query.lower()
    return not any(term in query_lower for term in non_educational)

def get_response_from_query(query: str) -> str:
    """
    Gera resposta educacional ULTRA DETALHADA com exemplos passo a passo completos
    """
    try:
        print(f"🎓 Processando pergunta com máximo detalhamento: {query[:50]}...")
        
        # Verificação educacional
        if not is_educational_query(query):
            return """
🎓 Como tutor educacional ULTRA detalhado, foco em questões de aprendizado!

📚 POSSO ENSINAR DETALHADAMENTE:
• Matemática: álgebra, geometria, cálculo, estatística
• Física: mecânica, termodinâmica, eletromagnetismo
• Química: estequiometria, soluções, reações
• Biologia: genética, ecologia, fisiologia
• Métodos de resolução de problemas

🎯 MEU MÉTODO ULTRA DETALHADO INCLUI:
✅ Explicação completa de conceitos
✅ Todas as fórmulas necessárias
✅ Métodos passo a passo muito detalhados
✅ Múltiplos exemplos resolvidos completamente
✅ Orientação detalhada para aplicação

🤔 Reformule sua pergunta para algo educacional!
            """
        
        # Verificar sistema
        if not setup_llama_index():
            return """
❌ Sistema não disponível no momento.

🎓 METODOLOGIA GERAL ULTRA DETALHADA:

🎯 ANÁLISE COMPLETA: 
1. Identifique tipo de problema e conceitos envolvidos
2. Liste todos os dados e o que se procura
3. Determine estratégia de abordagem

📚 ESTUDO DETALHADO: 
1. Domine conceitos fundamentais necessários
2. Compreenda todas as fórmulas aplicáveis
3. Entenda quando usar cada método

🛠️ APLICAÇÃO PASSO A PASSO:
1. Organize dados sistematicamente
2. Aplique conceitos na sequência correta
3. Execute cálculos com verificação
4. Interprete resultados obtidos

📝 EXEMPLOS COMPLETOS:
1. Resolva problemas similares
2. Varie tipos para fixar conceitos
3. Use métodos alternativos

🔍 VERIFICAÇÃO DETALHADA:
1. Confira cada etapa
2. Use métodos alternativos
3. Analise coerência dos resultados

Configure GROQ_API_KEY e tente novamente!
            """
        
        # Obter base de conhecimento
        index = get_index()
        if index is None:
            return "❌ Base de conhecimento não disponível."
        
        # Configurar query engine para respostas mais longas e detalhadas
        query_engine = index.as_query_engine(
            similarity_top_k=5,  # Mais contexto
            response_mode="tree_summarize",  # Melhor para respostas longas
            streaming=False
        )
        
        # Prompt educacional ULTRA detalhado
        ultra_detailed_prompt = f"""
{ULTRA_DETAILED_EDUCATIONAL_PROMPT}

PERGUNTA DO ESTUDANTE: {query}

IMPORTANTE: 
- Forneça uma resposta EXTREMAMENTE DETALHADA
- Inclua pelo menos 2-3 exemplos COMPLETOS resolvidos passo a passo
- Explique CADA etapa minuciosamente
- Dê TODOS os conceitos e fórmulas necessários
- Oriente detalhadamente para aplicação no problema específico
- NÃO resolva completamente o problema específico perguntado

Sua resposta deve ser um guia ULTRA COMPLETO de aprendizado!
        """
        
        print("🔄 Gerando resposta educacional ULTRA detalhada...")
        
        try:
            response = query_engine.query(ultra_detailed_prompt)
            result = str(response)
            
            # Verificar se tem conteúdo educacional suficiente
            if len(result) < 500:  # Se resposta muito curta, complementar
                result = f"""
🎯 ANÁLISE COMPLETA DO PROBLEMA: {query}

{result}

📚 COMPLEMENTO EDUCACIONAL DETALHADO:

🛠️ MÉTODO GERAL PASSO A PASSO:
Passo 1: ANÁLISE E IDENTIFICAÇÃO
- Leia cuidadosamente o problema
- Identifique tipo de problema e conceitos envolvidos
- Liste todos os dados fornecidos
- Determine claramente o que se procura

Passo 2: CONCEITOS FUNDAMENTAIS
- Revise todos os conceitos necessários
- Compreenda as definições importantes
- Identifique fórmulas aplicáveis
- Entenda quando usar cada método

Passo 3: ESTRATÉGIA DE RESOLUÇÃO
- Escolha a abordagem mais adequada
- Organize os dados sistematicamente
- Planeje a sequência de cálculos
- Prepare métodos de verificação

Passo 4: APLICAÇÃO PRÁTICA
- Execute cada etapa cuidadosamente
- Mostre todos os cálculos
- Explique cada operação realizada
- Mantenha organização clara

Passo 5: VERIFICAÇÃO E INTERPRETAÇÃO
- Confira todos os cálculos
- Verifique coerência dos resultados
- Interprete o significado físico/matemático
- Compare com estimativas iniciais

🎯 APLICAÇÃO NO SEU PROBLEMA:
Agora você pode aplicar esta metodologia detalhada no seu problema específico, seguindo cada passo cuidadosamente!
                """
            
            print("✅ Resposta educacional ULTRA detalhada gerada")
            return result
            
        except Exception as e:
            print(f"❌ Erro na consulta: {e}")
            return f"""
🎓 GUIA EDUCACIONAL ULTRA DETALHADO PARA: "{query}"

🎯 METODOLOGIA UNIVERSAL DE RESOLUÇÃO DETALHADA:

📚 FASE 1 - ANÁLISE COMPLETA:
1. 🔍 IDENTIFICAÇÃO DETALHADA:
   - Que tipo específico de problema é este?
   - Quais conceitos fundamentais estão envolvidos?
   - Que área do conhecimento abrange?
   - Qual o nível de complexidade?

2. 📖 MAPEAMENTO DE CONHECIMENTOS:
   - Como se relaciona com conhecimentos anteriores?
   - Quais pré-requisitos são necessários?
   - Onde se aplica na prática?

📐 FASE 2 - CONCEITOS E FÓRMULAS DETALHADOS:
1. 🧮 FÓRMULAS FUNDAMENTAIS:
   - Identifique TODAS as fórmulas aplicáveis
   - Compreenda cada variável e sua unidade
   - Entenda quando usar cada fórmula
   - Memorize relações importantes

2. 📝 CONCEITOS ESSENCIAIS:
   - Defina claramente cada conceito
   - Compreenda propriedades e características
   - Identifique limitações e aplicações
   - Conecte com outros conceitos

🛠️ FASE 3 - ESTRATÉGIA DETALHADA:
1. 🎯 PLANEJAMENTO:
   - Organize todos os dados disponíveis
   - Determine estratégia de abordagem
   - Escolha métodos mais adequados
   - Prepare verificações

2. 🔄 EXECUÇÃO SISTEMÁTICA:
   - Execute cada etapa metodicamente
   - Documente todos os cálculos
   - Explique cada operação
   - Mantenha organização clara

📝 FASE 4 - EXEMPLOS PRÁTICOS COMPLETOS:
[Aqui incluiria 2-3 exemplos similares resolvidos completamente]

🔍 FASE 5 - VERIFICAÇÃO RIGOROSA:
1. ✅ CONFERÊNCIA DE CÁLCULOS:
   - Refaça operações críticas
   - Use métodos alternativos
   - Verifique unidades de medida
   - Analise ordem de grandeza

2. 🤔 ANÁLISE DE COERÊNCIA:
   - O resultado faz sentido?
   - Está dentro do esperado?
   - Atende às condições do problema?
   - Tem interpretação física/matemática válida?

🎯 APLICAÇÃO NO SEU CASO ESPECÍFICO:
Siga esta metodologia detalhada para resolver seu problema passo a passo!

Erro técnico: {str(e)[:100]}...
            """
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return f"""
🎓 SISTEMA EDUCACIONAL ULTRA DETALHADO PARA: "{query}"

📚 MÉTODO CIENTÍFICO DE APRENDIZADO AVANÇADO:

🎯 MÓDULO 1 - ANÁLISE PROFUNDA DO PROBLEMA:
• Identifique claramente o que é solicitado
• Reconheça o tipo e subtipo de problema
• Liste todas as informações disponíveis
• Determine o contexto e aplicação

📐 MÓDULO 2 - ARSENAL DE FERRAMENTAS:
• Conceitos teóricos fundamentais necessários
• Todas as fórmulas e equações aplicáveis
• Métodos de cálculo e estratégias
• Técnicas de verificação e conferência

🛠️ MÓDULO 3 - PROCESSO DE RESOLUÇÃO SISTEMÁTICO:
1. 📋 ORGANIZAÇÃO COMPLETA:
   - Dados fornecidos e suas unidades
   - Incógnitas procuradas
   - Relações entre variáveis
   - Restrições e limitações

2. 🎯 PLANEJAMENTO ESTRATÉGICO:
   - Sequência lógica de abordagem
   - Métodos mais eficientes
   - Pontos críticos de atenção
   - Estratégias de verificação

3. 🧮 EXECUÇÃO DETALHADA:
   - Aplicação passo a passo
   - Cálculos organizados e documentados
   - Verificações intermediárias
   - Interpretação de resultados parciais

4. ✅ FINALIZAÇÃO E VERIFICAÇÃO:
   - Conferência completa dos cálculos
   - Análise de coerência dos resultados
   - Verificação por métodos alternativos
   - Interpretação final contextualizada

📝 MÓDULO 4 - EXEMPLOS EDUCATIVOS:
• Resolva problemas variados similares
• Entenda padrões e metodologias
• Pratique diferentes abordagens
• Desenvolva intuição matemática/científica

🔍 MÓDULO 5 - CONSOLIDAÇÃO:
• Revise conceitos fundamentais
• Pratique aplicações diversas
• Conecte com conhecimentos prévios
• Prepare-se para variações do problema

🎯 APLICAÇÃO PRÁTICA GUIADA:
Agora você tem um framework completo para abordar seu problema específico de forma sistemática e detalhada!

Erro do sistema: {str(e)}
        """

def update_index():
    """Atualiza base educacional"""
    global _index
    
    try:
        print("🔄 Atualizando base educacional ULTRA detalhada...")
        
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

# Inicialização do sistema educacional ULTRA DETALHADO
print("🎓 Inicializando Pensa.AI - SISTEMA EDUCACIONAL ULTRA DETALHADO...")
print("📋 CARACTERÍSTICAS AVANÇADAS:")
print("   ✅ Explicações extremamente detalhadas")
print("   ✅ Múltiplos exemplos resolvidos passo a passo")
print("   ✅ Fórmulas completas com explicações")
print("   ✅ Métodos de resolução ultra detalhados")
print("   ✅ Orientação detalhada para aplicação")
print("   ❌ NÃO dá resultado final do problema específico")
print("   🧠 Usa modelo Llama3-70B para máxima qualidade")

try:
    if setup_llama_index():
        ensure_directories()
        get_index()
        print("✅ Sistema EDUCACIONAL ULTRA DETALHADO pronto!")
        print("🎯 Missão: Ensinar TUDO com máximo detalhamento!")
    else:
        print("⚠️ Sistema com limitações - verifique GROQ_API_KEY")
except Exception as e:
    print(f"❌ Erro na inicialização: {e}")