# backend/app/llama_index_helper.py - VERSÃO CORRIGIDA COM LLAMA + GROQ

import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Importações do LlamaIndex com tratamento de erros
try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        Settings,
        Document,
        load_index_from_storage
    )
    from llama_index.llms.groq import Groq
    LLAMA_INDEX_AVAILABLE = True
    print("✅ LlamaIndex importado com sucesso")
except ImportError as e:
    print(f"⚠️ LlamaIndex não disponível: {e}")
    print("💡 Execute: pip install llama-index llama-index-llms-groq")
    LLAMA_INDEX_AVAILABLE = False

# Importação do Groq direto como fallback
try:
    from groq import Groq as GroqClient
    GROQ_AVAILABLE = True
    print("✅ Groq importado com sucesso")
except ImportError as e:
    print(f"❌ Groq não disponível: {e}")
    print("💡 Execute: pip install groq")
    GROQ_AVAILABLE = False

# Diretórios usados
PERSIST_DIR = "backend/index"
UPLOADS_DIR = "backend/data/uploads"

# Variáveis globais
_index = None
_initialized = False
_groq_client = None

# PROMPT EDUCACIONAL OTIMIZADO
OPTIMIZED_EDUCATIONAL_PROMPT = """
VOCÊ É O PENSA.AI - TUTOR EDUCACIONAL ESPECIALISTA

MISSÃO: Ensinar detalhadamente com exemplos passo a passo, mas SEM dar o resultado final.
VOCE É UM TUTOR QUE ENSINA, NÃO RESOLVE PROBLEMAS DIRETAMENTE.
VOCÊ NÃO DÁ A RESPOSTA FINAL, APENAS ORIENTA O ALUNO A RESOLVER.
VOCÊ EXPLICA PASSO A PASSO, DANDO EXEMPLOS COMPLETOS, MAS SEM DAR O RESULTADO FINAL DO PROBLEMA ESPECÍFICO.

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
    if not LLAMA_INDEX_AVAILABLE:
        print("⚠️ LlamaIndex não disponível, pulando embedding")
        return False
    
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
        print("⚠️ HuggingFace embeddings não disponível, usando padrão")
        return True
    except Exception as e:
        print(f"⚠️ Erro no embedding: {e}")
        return True

def setup_groq_client():
    """Configura cliente Groq direto"""
    global _groq_client
    
    if not GROQ_AVAILABLE:
        return False
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY não encontrada")
        return False
    
    try:
        _groq_client = GroqClient(api_key=groq_api_key)
        
        # Teste de conectividade
        test_response = _groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "teste"}],
            max_tokens=3
        )
        print("✅ Groq client direto funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro Groq client: {e}")
        return False

def setup_llama_index():
    """Configura LlamaIndex otimizado"""
    global _initialized
    
    if _initialized:
        return True
    
    if not LLAMA_INDEX_AVAILABLE:
        print("⚠️ LlamaIndex não disponível, usando apenas Groq")
        return setup_groq_client()
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY não encontrada no arquivo .env")
        return False
    
    try:
        # Configurar embedding primeiro
        setup_embedding_model()
        
        # Configurações OTIMIZADAS para evitar erro de contexto
        llm = Groq(
            model="llama3-8b-8192",  # Modelo mais estável
            api_key=groq_api_key,
            temperature=0.2,
            max_tokens=1500,  # Reduzido para evitar overflow
            timeout=30,
        )
        
        Settings.llm = llm
        
        # Configurações do índice para respostas mais concisas
        Settings.chunk_size = 256  # Chunks bem menores
        Settings.chunk_overlap = 25  # Overlap reduzido
        
        # Teste de conectividade
        print("🧪 Testando LlamaIndex + Groq...")
        test_response = llm.complete("Teste rápido")
        print("✅ LlamaIndex + Groq funcionando!")
        
        # Configurar também cliente direto como backup
        setup_groq_client()
        
        _initialized = True
        print("✅ Sistema educacional HÍBRIDO configurado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar LlamaIndex: {str(e)}")
        print("🔄 Tentando apenas Groq direto...")
        return setup_groq_client()

def ensure_directories():
    """Garante diretórios necessários"""
    try:
        directories = [UPLOADS_DIR, PERSIST_DIR, "./embeddings_cache"]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Erro ao criar diretórios: {str(e)}")
        return False

def create_optimized_educational_index():
    """Cria índice educacional otimizado"""
    if not LLAMA_INDEX_AVAILABLE:
        return None
        
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
    if not LLAMA_INDEX_AVAILABLE:
        return None
        
    try:
        ensure_directories()
        
        documents = []
        
        # Carregar PDFs educacionais se existirem
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
{doc.text[:1000]}  

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
        
        # Base educacional sempre incluída
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
        
        print(f"✅ Base educacional com {len(documents)} recursos")
        return index
        
    except Exception as e:
        print(f"❌ Erro ao construir base: {str(e)}")
        return create_optimized_educational_index()

def get_index():
    """Retorna índice educacional"""
    global _index
    
    if not LLAMA_INDEX_AVAILABLE:
        return None
    
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
        _index = create_optimized_educational_index()
        return _index

def is_educational_query(query: str) -> bool:
    """Verificação para perguntas educacionais"""
    non_educational = [
        'clima hoje', 'temperatura agora', 'notícias atuais',
        'que horas são', 'data de hoje', 'como vai você'
    ]
    
    query_lower = query.lower()
    return not any(term in query_lower for term in non_educational)

def generate_groq_fallback(query: str) -> str:
    """Gera resposta usando apenas Groq direto"""
    if not _groq_client:
        return generate_basic_fallback(query)
    
    try:
        full_prompt = f"""
{OPTIMIZED_EDUCATIONAL_PROMPT}

PERGUNTA DO ESTUDANTE: {query}

Responda seguindo exatamente a estrutura educacional apresentada.
        """
        
        response = _groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=1500,
            temperature=0.2
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Erro Groq fallback: {e}")
        return generate_basic_fallback(query)

def generate_basic_fallback(query: str) -> str:
    """Resposta básica quando tudo falha"""
    return f"""
🎓 PENSA.AI - SISTEMA EDUCACIONAL

📚 **Sobre sua pergunta**: "{query[:100]}..."

🎯 **METODOLOGIA GERAL**:
1. **IDENTIFIQUE**: Que tipo de problema é
2. **ORGANIZE**: Dados conhecidos e incógnitas
3. **APLIQUE**: Conceitos e fórmulas adequadas
4. **RESOLVA**: Passo a passo sistematicamente
5. **VERIFIQUE**: Se o resultado faz sentido

💡 **ESTRATÉGIA RECOMENDADA**:
- Determine a área de estudo (matemática, física, etc.)
- Revise conceitos fundamentais relacionados
- Procure exemplos similares resolvidos
- Aplique metodicamente os procedimentos

🔧 **Nota técnica**: Sistema funcionando em modo básico. Para funcionalidade completa, verifique as configurações.
    """

def get_response_from_query(query: str) -> str:
    """Gera resposta educacional - VERSÃO HÍBRIDA"""
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
        
        # Tentar configurar sistema se ainda não foi
        if not _initialized:
            setup_llama_index()
        
        # OPÇÃO 1: Tentar LlamaIndex (preferido)
        if LLAMA_INDEX_AVAILABLE and _initialized:
            index = get_index()
            if index is not None:
                try:
                    # Configurar query engine OTIMIZADO
                    query_engine = index.as_query_engine(
                        similarity_top_k=1,  # Apenas 1 resultado para evitar overflow
                        response_mode="compact"
                    )
                    
                    # Prompt mais conciso
                    optimized_prompt = f"""
{OPTIMIZED_EDUCATIONAL_PROMPT[:500]}

PERGUNTA: {query}

Resposta educacional estruturada:
                    """
                    
                    print("🔄 Usando LlamaIndex...")
                    response = query_engine.query(optimized_prompt)
                    result = str(response)
                    
                    if len(result) > 200 and "🎯" in result:
                        print("✅ Resposta LlamaIndex gerada")
                        return result
                    else:
                        print("⚠️ Resposta LlamaIndex inadequada, usando fallback")
                        
                except Exception as e:
                    print(f"❌ Erro LlamaIndex: {e}")
        
        # OPÇÃO 2: Fallback Groq direto
        print("🔄 Usando Groq direto...")
        return generate_groq_fallback(query)
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return generate_basic_fallback(query)

def update_index():
    """Atualiza base educacional"""
    global _index
    
    if not LLAMA_INDEX_AVAILABLE:
        print("⚠️ LlamaIndex não disponível para atualizar")
        return False
    
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

# Inicialização
print("🎓 Inicializando Pensa.AI - SISTEMA HÍBRIDO...")
print("📋 CARACTERÍSTICAS:")
print("   ✅ Respostas detalhadas e estruturadas")
print("   ✅ Exemplos resolvidos passo a passo")
print("   ✅ Sistema híbrido: LlamaIndex + Groq fallback")
print("   ✅ Otimizado para evitar erros de contexto")
print("   ❌ NÃO dá resultado final do problema específico")

try:
    if setup_llama_index():
        if LLAMA_INDEX_AVAILABLE:
            ensure_directories()
            get_index()
            print("✅ Sistema HÍBRIDO COMPLETO pronto!")
        else:
            print("✅ Sistema GROQ APENAS pronto!")
    else:
        print("⚠️ Sistema com limitações - verifique GROQ_API_KEY")
except Exception as e:
    print(f"❌ Erro na inicialização: {e}")