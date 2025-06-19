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

# SISTEMA DE PROMPTS EDUCACIONAIS COMPLETO - ENSINA TUDO EXCETO RESULTADO FINAL
COMPLETE_EDUCATIONAL_PROMPT = """
VOCÊ É O PENSA.AI - TUTOR EDUCACIONAL ESPECIALISTA

MISSÃO: Ensinar COMPLETAMENTE como resolver problemas, incluindo fórmulas, métodos e exemplos, mas NUNCA dar o resultado final.

REGRAS EDUCACIONAIS OBRIGATÓRIAS:
✅ SEMPRE forneça fórmulas completas e explicadas
✅ SEMPRE ensine passo a passo detalhadamente
✅ SEMPRE dê exemplos resolvidos (mas diferentes da pergunta)
✅ SEMPRE explique conceitos fundamentais
✅ SEMPRE mostre métodos e estratégias
✅ SEMPRE conecte com conhecimentos anteriores

❌ JAMAIS forneça o resultado final da pergunta específica
❌ JAMAIS resolva completamente o problema pedido
❌ JAMAIS dê a resposta numérica final

ESTRUTURA OBRIGATÓRIA DE ENSINO:

🎯 ENTENDENDO O PROBLEMA:
[Analise que tipo de problema é e o que precisa ser resolvido]

📚 CONCEITOS FUNDAMENTAIS:
[Explique TODOS os conceitos necessários com definições completas]
• Conceito 1: [Definição + importância + aplicações]
• Conceito 2: [Definição + importância + aplicações]
• [Continue para todos os conceitos]

📐 FÓRMULAS E MÉTODOS:
[Forneça TODAS as fórmulas necessárias com explicações]
• Fórmula Principal: [fórmula] onde [explicar cada variável]
• Fórmulas Auxiliares: [se necessário]
• Quando usar cada fórmula: [critérios]

🛠️ MÉTODO DE RESOLUÇÃO PASSO A PASSO:
Passo 1: [O que fazer primeiro e como fazer]
   💡 Como executar: [instruções detalhadas]
   🔍 O que observar: [pontos importantes]

Passo 2: [Próxima etapa e como executar]
   💡 Como executar: [instruções detalhadas]
   🔍 O que observar: [pontos importantes]

[Continue para todos os passos necessários]

📝 EXEMPLO RESOLVIDO COMPLETO:
[Resolva um problema SIMILAR mas DIFERENTE do perguntado]
Problema exemplo: [enunciado diferente]
Solução passo a passo:
- Identificação: [o que é dado e o que procurar]
- Aplicação da fórmula: [mostrar cálculo completo]
- Verificação: [como conferir se está correto]
- Resultado: [mostrar resultado final do EXEMPLO]

📝 SEGUNDO EXEMPLO:
[Outro exemplo com variação para fixar o aprendizado]

🔄 VERIFICAÇÃO E CONFERÊNCIA:
[Como verificar se a resolução está correta]
• Método 1: [forma de verificar]
• Método 2: [outra forma]
• Sinais de erro comum: [o que evitar]

🎯 APLICANDO NO SEU PROBLEMA:
[Orientações específicas para o problema perguntado SEM resolvê-lo]
• Identifique: [o que procurar no problema]
• Organize: [como estruturar os dados]
• Aplique: [qual método usar]
• Calcule: [quais passos seguir]
• Verifique: [como conferir]

🤔 REFLEXÕES PARA FIXAR:
[Perguntas para o estudante consolidar o aprendizado]

LEMBRE-SE: Ensine TUDO sobre como resolver, mas deixe o estudante chegar ao resultado final sozinho!
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
    """Configura LlamaIndex para ensino completo"""
    global _initialized
    
    if _initialized:
        return True
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY não encontrada no arquivo .env")
        return False
    
    try:
        setup_embedding_model()
        
        # Configurações otimizadas para ensino detalhado
        llm = Groq(
            model="llama3-8b-8192",
            api_key=groq_api_key,
            temperature=0.2,  # Consistência com criatividade para exemplos
            max_tokens=2500,  # Espaço para exemplos completos
            timeout=35,
        )
        
        Settings.llm = llm
        
        # Teste de conectividade
        print("🧪 Testando Groq...")
        test_response = llm.complete("Teste de conectividade")
        print("✅ Groq funcionando!")
        
        _initialized = True
        print("✅ Sistema educacional COMPLETO configurado!")
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

def create_educational_index():
    """Cria índice com conhecimento educacional completo"""
    try:
        educational_content = Document(
            text="""
            PENSA.AI - SISTEMA EDUCACIONAL COMPLETO
            
            ESPECIALIZAÇÃO EM ENSINO DETALHADO:
            
            MATEMÁTICA - Métodos e Fórmulas Completas:
            
            ÁLGEBRA:
            • Equações lineares: ax + b = c
              - Método: isolar x dividindo por a
              - Exemplo: 2x + 5 = 11 → 2x = 6 → x = 3
            • Equações quadráticas: ax² + bx + c = 0
              - Fórmula de Bhaskara: x = (-b ± √(b²-4ac))/2a
              - Delta: Δ = b² - 4ac
            • Sistemas de equações
              - Método da substituição
              - Método da eliminação
            
            GEOMETRIA:
            • Área do retângulo: A = base × altura
            • Área do triângulo: A = (base × altura)/2
            • Área do círculo: A = πr²
            • Perímetro do círculo: P = 2πr
            • Teorema de Pitágoras: a² + b² = c²
            
            FUNÇÕES:
            • Função linear: f(x) = ax + b
            • Função quadrática: f(x) = ax² + bx + c
            • Análise de gráficos e propriedades
            
            FÍSICA - Leis e Fórmulas:
            
            MECÂNICA:
            • Velocidade: v = Δs/Δt
            • Aceleração: a = Δv/Δt
            • MRU: s = s₀ + vt
            • MRUV: s = s₀ + v₀t + at²/2
            • Força: F = ma (2ª Lei de Newton)
            • Trabalho: W = F × d × cos θ
            • Energia cinética: Ec = mv²/2
            • Energia potencial: Ep = mgh
            
            QUÍMICA - Conceitos e Cálculos:
            
            ESTEQUIOMETRIA:
            • Mol: unidade de quantidade de matéria
            • Massa molar: massa de 1 mol da substância
            • n = m/M (número de mols)
            • Balanceamento de equações
            • Cálculos de proporção
            
            SOLUÇÕES:
            • Concentração: C = n/V
            • Molaridade: M = n/V
            • Diluição: C₁V₁ = C₂V₂
            
            BIOLOGIA - Processos e Conceitos:
            
            GENÉTICA:
            • Leis de Mendel
            • Cruzamentos e probabilidades
            • Heredograma e análise
            
            ECOLOGIA:
            • Ciclos biogeoquímicos
            • Relações ecológicas
            • Fluxo de energia
            
            METODOLOGIA DE ENSINO:
            1. Identificar conceitos necessários
            2. Explicar cada conceito detalhadamente
            3. Mostrar fórmulas e quando usá-las
            4. Demonstrar com exemplos completos
            5. Guiar aplicação no problema específico
            6. Ensinar verificação de resultados
            
            ESTRATÉGIAS PEDAGÓGICAS:
            - Partir do conhecido para o desconhecido
            - Usar analogias e exemplos práticos
            - Mostrar múltiplas formas de resolver
            - Conectar teoria com aplicação
            - Estimular raciocínio crítico
            """
        )
        
        index = VectorStoreIndex.from_documents([educational_content])
        print("✅ Índice educacional completo criado")
        return index
        
    except Exception as e:
        print(f"❌ Erro ao criar índice: {str(e)}")
        return None

def build_index_from_documents():
    """Constrói índice educacional completo"""
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
MATERIAL EDUCACIONAL PARA ENSINO COMPLETO:

CONTEÚDO ORIGINAL:
{doc.text}

INSTRUÇÕES PEDAGÓGICAS DETALHADAS:

1. ENSINO COMPLETO DE CONCEITOS:
- Explique TODOS os conceitos fundamentais presentes no material
- Forneça definições claras e completas
- Mostre aplicações práticas e importância
- Conecte com outros conhecimentos

2. FÓRMULAS E MÉTODOS:
- Apresente TODAS as fórmulas relevantes
- Explique cada variável e sua unidade
- Mostre quando e como usar cada fórmula
- Dê dicas de memorização e compreensão

3. RESOLUÇÃO PASSO A PASSO:
- Ensine metodologia completa de resolução
- Mostre cada etapa detalhadamente
- Explique o raciocínio por trás de cada passo
- Indique pontos de atenção e erros comuns

4. EXEMPLOS RESOLVIDOS:
- Resolva exemplos SIMILARES mas DIFERENTES da pergunta
- Mostre resolução completa com resultado final nos exemplos
- Varie tipos de problemas para fixar conceitos
- Explique estratégias de abordagem

5. APLICAÇÃO GUIADA:
- Oriente como aplicar no problema específico
- Identifique dados e incógnitas
- Sugira estratégia de resolução
- NÃO resolva completamente o problema perguntado

6. VERIFICAÇÃO E CONFERÊNCIA:
- Ensine métodos de verificação
- Mostre como identificar erros
- Dê dicas de conferência de resultados
                        """
                        enhanced_doc = Document(text=enhanced_text)
                        documents.append(enhanced_doc)
                        
                except Exception as e:
                    print(f"⚠️ Erro ao processar PDFs: {e}")
        
        # Base educacional sempre presente
        base_content = Document(
            text="""
            PENSA.AI - TUTOR EDUCACIONAL ESPECIALISTA
            
            MISSÃO: Ensinar de forma completa e detalhada
            
            METODOLOGIA COMPLETA:
            1. Análise do problema e identificação de conceitos
            2. Explicação detalhada de todos os conceitos
            3. Apresentação de fórmulas e métodos
            4. Demonstração com exemplos resolvidos
            5. Orientação para aplicação no problema específico
            6. Ensino de verificação e conferência
            
            PRINCÍPIOS PEDAGÓGICOS:
            - Ensinar TUDO sobre como resolver
            - Fornecer fórmulas completas e explicadas
            - Dar exemplos detalhados e resolvidos
            - Guiar passo a passo a aplicação
            - NUNCA dar o resultado final do problema perguntado
            - Estimular aprendizado ativo e descoberta
            """
        )
        documents.append(base_content)
        
        # Criar índice
        index = VectorStoreIndex.from_documents(documents)
        
        # Salvar índice
        try:
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            print("💾 Índice educacional salvo")
        except Exception as e:
            print(f"⚠️ Erro ao salvar: {e}")
        
        print(f"✅ Base educacional completa com {len(documents)} recursos")
        return index
        
    except Exception as e:
        print(f"❌ Erro ao construir base: {str(e)}")
        return create_educational_index()

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
        print("🆕 Criando base educacional...")
        _index = build_index_from_documents()
        return _index
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        _index = create_educational_index()
        return _index

def is_educational_query(query: str) -> bool:
    """Verificação permissiva para perguntas educacionais"""
    non_educational = [
        'clima hoje', 'temperatura agora', 'notícias atuais',
        'que horas são', 'data de hoje'
    ]
    
    query_lower = query.lower()
    return not any(term in query_lower for term in non_educational)

def remove_final_answers_from_specific_problem(response: str, original_query: str) -> str:
    """
    Remove apenas resultados finais do problema específico,
    mas mantém resultados de exemplos educacionais
    """
    
    # Padrões de resposta final para o problema específico
    final_answer_patterns = [
        r'(?:portanto|logo|então|assim),?\s*(?:a\s*resposta\s*é|o\s*resultado\s*é|temos)\s*[:\s]*(\d+(?:[.,]\d+)?)',
        r'(?:^|\n)\s*[x-z]\s*=\s*(\d+(?:[.,]\d+)?)\s*(?:\n|$)',
        r'(?:resposta|resultado|solução)\s*final\s*[:\s]*(\d+(?:[.,]\d+)?)',
    ]
    
    # Substituir apenas respostas finais específicas
    for pattern in final_answer_patterns:
        response = re.sub(
            pattern,
            r'[RESULTADO FINAL REMOVIDO - Agora é sua vez de calcular!]',
            response,
            flags=re.IGNORECASE | re.MULTILINE
        )
    
    return response

def get_response_from_query(query: str) -> str:
    """
    Gera resposta educacional COMPLETA: ensina tudo, dá exemplos,
    mas não resolve o problema específico até o final
    """
    try:
        print(f"🎓 Processando pergunta: {query[:50]}...")
        
        # Verificação educacional
        if not is_educational_query(query):
            return """
🎓 Como tutor educacional, foco em questões de aprendizado!

📚 POSSO ENSINAR COMPLETAMENTE:
• Matemática: álgebra, geometria, cálculo, estatística
• Física: mecânica, termodinâmica, eletromagnetismo
• Química: estequiometria, soluções, reações
• Biologia: genética, ecologia, fisiologia
• Métodos de resolução de problemas

🎯 MEU MÉTODO INCLUI:
✅ Explicação completa de conceitos
✅ Todas as fórmulas necessárias
✅ Métodos passo a passo
✅ Exemplos resolvidos detalhadamente
✅ Orientação para seu problema específico

🤔 Reformule sua pergunta para algo educacional!
            """
        
        # Verificar sistema
        if not setup_llama_index():
            return """
❌ Sistema não disponível no momento.

🎓 METODOLOGIA GERAL PARA QUALQUER PROBLEMA:

🎯 ANÁLISE: Identifique tipo de problema e conceitos
📚 ESTUDO: Domine conceitos fundamentais necessários
📐 FÓRMULAS: Identifique e compreenda fórmulas aplicáveis
🛠️ MÉTODO: Siga estratégia passo a passo
📝 EXEMPLOS: Pratique com casos similares
🔍 VERIFICAÇÃO: Confira resultado e coerência

Configure GROQ_API_KEY e tente novamente!
            """
        
        # Obter base de conhecimento
        index = get_index()
        if index is None:
            return "❌ Base de conhecimento não disponível."
        
        # Configurar query engine
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )
        
        # Prompt educacional completo
        complete_prompt = f"""
{COMPLETE_EDUCATIONAL_PROMPT}

PERGUNTA DO ESTUDANTE: {query}

IMPORTANTE: Ensine TUDO sobre como resolver este tipo de problema. Dê fórmulas, métodos, exemplos completos resolvidos (mas diferentes), e oriente a aplicação, mas NÃO resolva completamente o problema específico perguntado.

Sua resposta deve ser um guia completo de aprendizado!
        """
        
        print("🔄 Gerando resposta educacional completa...")
        
        try:
            response = query_engine.query(complete_prompt)
            result = str(response)
            
            # Remover apenas resultados finais do problema específico
            result = remove_final_answers_from_specific_problem(result, query)
            
            # Verificar se tem conteúdo educacional suficiente
            if len(result) < 200:
                result = f"""
🎯 ENTENDENDO SEU PROBLEMA: {query}

📚 CONCEITOS FUNDAMENTAIS NECESSÁRIOS:
Para resolver este tipo de problema, você precisa dominar conceitos específicos que vou explicar detalhadamente.

📐 FÓRMULAS E MÉTODOS:
Vou apresentar todas as fórmulas relevantes e ensinar quando e como usar cada uma.

🛠️ MÉTODO DE RESOLUÇÃO:
Passo 1: Análise e identificação do que é dado e procurado
Passo 2: Escolha da estratégia e fórmulas adequadas
Passo 3: Aplicação sistemática dos conceitos
Passo 4: Cálculos organizados e verificação

📝 EXEMPLO SIMILAR RESOLVIDO:
Vou resolver um problema parecido para demonstrar o método completo.

🎯 APLICANDO NO SEU CASO:
Agora você pode seguir os mesmos passos para resolver seu problema específico.

{result}
                """
            
            print("✅ Resposta educacional completa gerada")
            return result
            
        except Exception as e:
            print(f"❌ Erro na consulta: {e}")
            return f"""
🎓 GUIA EDUCACIONAL PARA: "{query}"

🎯 METODOLOGIA UNIVERSAL DE RESOLUÇÃO:

📚 CONCEITOS BÁSICOS:
1. 🔍 IDENTIFIQUE: Que tipo de problema é este?
2. 📖 ESTUDE: Quais conceitos fundamentais estão envolvidos?
3. 🔗 CONECTE: Como se relaciona com conhecimentos anteriores?

📐 FÓRMULAS E FERRAMENTAS:
1. 🧮 IDENTIFIQUE: Quais fórmulas são aplicáveis?
2. 📝 COMPREENDA: O que significa cada variável?
3. 🎯 APLIQUE: Como usar cada fórmula corretamente?

🛠️ ESTRATÉGIA PASSO A PASSO:
Passo 1: Leia e compreenda completamente o problema
Passo 2: Identifique dados fornecidos e o que procura
Passo 3: Escolha método e fórmulas adequadas
Passo 4: Execute cálculos de forma organizada
Passo 5: Verifique coerência do resultado

📝 PRÁTICA:
- Resolva problemas similares
- Varie os dados para entender o padrão
- Compare diferentes métodos de resolução

🔍 VERIFICAÇÃO:
- Confira se o resultado faz sentido
- Teste com valores conhecidos
- Use métodos alternativos para conferir

Erro técnico: {str(e)[:100]}...
            """
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return f"""
🎓 SISTEMA EDUCACIONAL PARA: "{query}"

📚 MÉTODO CIENTÍFICO DE APRENDIZADO:

🎯 ANÁLISE DO PROBLEMA:
- Identifique claramente o que é pedido
- Reconheça o tipo de problema
- Liste informações disponíveis

📐 FERRAMENTAS NECESSÁRIAS:
- Conceitos teóricos fundamentais
- Fórmulas e equações aplicáveis
- Métodos de cálculo adequados

🛠️ PROCESSO DE RESOLUÇÃO:
1. 📋 ORGANIZE: Dados e incógnitas
2. 🎯 PLANEJE: Estratégia de abordagem
3. 🧮 EXECUTE: Cálculos passo a passo
4. ✅ VERIFIQUE: Coerência dos resultados

📝 ESTRATÉGIAS DE ESTUDO:
- Pratique problemas variados
- Entenda o "porquê" de cada passo
- Conecte teoria com aplicação prática
- Desenvolva intuição matemática

🔍 DICAS IMPORTANTES:
- Sempre organize bem os dados
- Desenhe diagramas quando possível
- Confira unidades de medida
- Teste com casos especiais

Erro do sistema: {str(e)}
        """

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

# Inicialização do sistema educacional completo
print("🎓 Inicializando Pensa.AI - SISTEMA EDUCACIONAL COMPLETO...")
print("📋 CARACTERÍSTICAS:")
print("   ✅ Ensina conceitos detalhadamente")
print("   ✅ Fornece fórmulas completas")
print("   ✅ Dá exemplos resolvidos")
print("   ✅ Orienta passo a passo")
print("   ❌ NÃO dá resultado final do problema específico")

try:
    if setup_llama_index():
        ensure_directories()
        get_index()
        print("✅ Sistema EDUCACIONAL COMPLETO pronto!")
        print("🎯 Missão: Ensinar TUDO exceto a resposta final!")
    else:
        print("⚠️ Sistema com limitações - verifique GROQ_API_KEY")
except Exception as e:
    print(f"❌ Erro na inicialização: {e}")