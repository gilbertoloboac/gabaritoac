import json
from django.core.management.base import BaseCommand
from wagtail.models import Page
from home.models import SobrePage, ContatoPage, PoliticaPrivacidadePage


SOBRE_BODY = [
    {
        "type": "paragrafo",
        "value": "<h2>Quem Somos</h2><p>O <strong>GabaritoAC</strong> é o maior portal de notícias sobre educação, concursos e processos seletivos do estado do Acre. Nascemos com o propósito de democratizar o acesso à informação educacional, reunindo em um único lugar editais, resultados, vestibulares e oportunidades de capacitação para toda a comunidade acreana.</p>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>Nossa Missão</h2><p>Nossa missão é <strong>informar com qualidade, agilidade e responsabilidade</strong>, garantindo que candidatos, estudantes e profissionais da educação tenham acesso rápido e confiável a tudo o que precisam para tomar decisões importantes em suas carreiras acadêmicas e profissionais.</p><ul><li><strong>Acessibilidade:</strong> Conteúdo organizado e fácil de navegar para todos os públicos.</li><li><strong>Confiabilidade:</strong> Informações verificadas diretamente nas fontes oficiais (UFAC, IFAC, Governos Federal, Estadual e Municipal).</li><li><strong>Agilidade:</strong> Editais e resultados publicados em tempo real assim que disponibilizados.</li></ul>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>O Que Cobrimos</h2><p>O GabaritoAC abrange diversas áreas da educação no Acre:</p><ol><li><strong>Editais e Concursos:</strong> Publicações oficiais de processos seletivos da UFAC, IFAC, prefeituras e órgãos públicos estaduais e federais.</li><li><strong>Vestibular e SISU:</strong> Todas as informações sobre o vestibular da UFAC, inscrições no SISU e processos de acesso ao ensino superior.</li><li><strong>Cursos e Capacitação:</strong> Oportunidades de formação continua, cursos gratuitos e programas de capacitação disponíveis no estado.</li><li><strong>Educação Básica:</strong> Notícias relevantes sobre a rede pública e privada de educação no Acre.</li></ol>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>Nosso Canal no WhatsApp</h2><p>Para manter você sempre atualizado, criamos um <strong>canal exclusivo no WhatsApp</strong> onde enviamos diariamente as principais notícias sobre editais, concursos e oportunidades educacionais. É rápido, gratuito e direto no seu celular. <a href=\"https://whatsapp.com/channel/0029VbDJLSR3bbV8Vzsnka3v\" target=\"_blank\" rel=\"noopener noreferrer\">Inscreva-se agora!</a></p>"
    },
    {
        "type": "citacao",
        "value": "A educação é a arma mais poderosa que você pode usar para mudar o mundo. — Nelson Mandela"
    },
    {
        "type": "paragrafo",
        "value": "<h2>Equipe</h2><p>O GabaritoAC é mantido por uma equipe dedicada de profissionais da educação e da tecnologia da informação, comprometidos em manter o portal atualizado e funcionando com excelência. Trabalhamos com o objetivo de ser a referência em informações educacionais no estado do Acre.</p><p>Se você tem sugestões, correções ou quer entrar em contato conosco, acesse nossa <a href=\"/contato/\">página de contato</a> ou envie um e-mail para <strong>contato@gabaritoac.com.br</strong>.</p>"
    },
]

CONTATO_BODY = [
    {
        "type": "paragrafo",
        "value": "<h2>Fale Conosco</h2><p>Estamos à disposição para ouvir você. Se tem dúvidas, sugestões, correções ou quer divulgar um edital ou oportunidade, entre em contato conosco pelos canais abaixo.</p>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>Canais de Atendimento</h2><ul><li><strong>E-mail Geral:</strong> contato@gabaritoac.com.br</li><li><strong>E-mail Editorial:</strong> editorial@gabaritoac.com.br</li><li><strong>WhatsApp:</strong> <a href=\"https://whatsapp.com/channel/0029VbDJLSR3bbV8Vzsnka3v\" target=\"_blank\" rel=\"noopener noreferrer\">Canal oficial no WhatsApp</a></li></ul>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>Divulgue seu Edital</h2><p>Se você é de uma instituição pública e deseja divulgar um edital, concurso ou processo seletivo no GabaritoAC, envie a publicação oficial para <strong>editorial@gabaritoac.com.br</strong> com o assunto \"Divulgação de Edital\". Avaliaremos e publicaremos gratuitamente.</p>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>Encarregado de Dados (DPO)</h2><p>Para exercer seus direitos como titular de dados pessoais conforme a <strong>Lei Geral de Proteção de Dados (LGPD, Art. 18)</strong> — como acessar, corrigir ou solicitar a exclusão dos seus dados pessoais — entre em contato com nosso Encarregado:</p><p>E-mail: <strong>dpo@gabaritoac.com.br</strong></p><p>Responderemos em até 15 dias úteis, conforme Art. 19 da LGPD.</p>"
    },
]

PRIVACIDADE_BODY = [
    {
        "type": "paragrafo",
        "value": "<h2>Política de Privacidade</h2><p><strong>Última atualização:</strong> Janeiro de 2026</p><p>A sua privacidade é importante para nós. Esta Política de Privacidade descreve como o <strong>GabaritoAC</strong> coleta, usa e protege as informações dos seus usuários, em conformidade com a <strong>Lei Geral de Proteção de Dados (Lei nº 13.709/2018 — LGPD)</strong>.</p>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>1. Informações Coletadas</h2><p>Podemos coletar os seguintes tipos de dados:</p><ul><li><strong>Dados de navegação:</strong> Endereço IP, tipo de navegador, sistema operacional, páginas visitadas e tempo de permanência, coletados automaticamente via cookies e ferramentas de análise.</li><li><strong>Dados fornecidos voluntariamente:</strong> Nome e número de WhatsApp, caso você se inscreva em nosso canal de notícias.</li></ul>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>2. Uso das Informações</h2><p>As informações coletadas são utilizadas para:</p><ul><li>Melhorar a experiência de navegação no portal.</li><li>Enviar notícias e atualizações sobre editais e concursos, caso você tenha se inscrito.</li><li>Gerar estatísticas de acesso para aprimorar nosso conteúdo.</li><li>Cumprir obrigações legais, quando aplicável.</li></ul>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>3. Cookies</h2><p>Utilizamos cookies próprios e de terceiros para:</p><ul><li>Manter sua preferência de modo escuro/claro.</li><li>Controlar o consentimento de cookies (LGPD).</li><li>Analisar o tráfego do site via ferramentas de analytics.</li></ul><p>Você pode gerenciar suas preferências de cookies a qualquer momento通过 o banner de consentimento exibido na primeira visita.</p>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>4. Compartilhamento de Dados</h2><p>Não vendemos, alugamos ou compartilhamos seus dados pessoais com terceiros para fins de marketing. Os dados podem ser compartilhados apenas nas seguintes situações:</p><ul><li>Quando exigido por lei ou ordem judicial.</li><li>Com prestadores de serviços que auxiliam na operação do portal (hospedagem, email), sob acordos de confidencialidade.</li></ul>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>5. Seus Direitos (LGPD)</h2><p>Conforme o Art. 18 da LGPD, você tem o direito de:</p><ul><li><strong>Confirmar</strong> a existência de tratamento dos seus dados.</li><li><strong>Acessar</strong> os seus dados pessoais.</li><li><strong>Corrigir</strong> dados incompletos ou desatualizados.</li><li><strong>Solicitar a exclusão</strong> dos seus dados pessoais.</li><li><strong>Solicitar a portabilidade</strong> dos seus dados.</li><li><strong>Revogar o consentimento</strong> a qualquer momento.</li></ul><p>Para exercer esses direitos, entre em contato com nosso Encarregado de Dados (DPO) pelo e-mail: <strong>dpo@gabaritoac.com.br</strong></p>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>6. Segurança dos Dados</h2><p>Adotamos medidas técnicas e administrativas adequadas para proteger seus dados pessoais contra acessos não autorizados, destruição, perda, alterações ou qualquer forma de tratamento inadequado ou ilícito.</p>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>7. Alterações nesta Política</h2><p>Esta Política de Privacidade pode ser atualizada periodicamente. As alterações serão publicadas nesta página com a data da última atualização. Recomendamos que você consulte esta página regularmente.</p>"
    },
    {
        "type": "paragrafo",
        "value": "<h2>8. Contato</h2><p>Se você tem dúvidas sobre esta Política de Privacidade, entre em contato conosco:</p><ul><li><strong>E-mail:</strong> contato@gabaritoac.com.br</li><li><strong>DPO:</strong> dpo@gabaritoac.com.br</li></ul>"
    },
]


class Command(BaseCommand):
    help = "Cria as páginas Sobre, Contato e Privacidade sob a HomePage"

    def _create_page(self, home, model_class, data):
        slug = data["slug"]
        existing = model_class.objects.filter(slug=slug).first()
        if existing:
            self.stdout.write(f"  {model_class.__name__} já existe (pk={existing.pk})")
            return

        page = model_class(**data["kwargs"])
        home.add_child(instance=page)
        revision = page.save_revision(user=None, log_action=True)
        revision.publish()
        page.refresh_from_db()
        self.stdout.write(self.style.SUCCESS(
            f"  {model_class.__name__} criada: pk={page.pk}, slug={page.slug}"
        ))

    def handle(self, *args, **options):
        home = Page.objects.filter(slug="home", depth=2).first()
        if not home:
            self.stderr.write("HomePage não encontrada.")
            return

        self.stdout.write("Criando páginas...")

        self._create_page(home, SobrePage, {
            "slug": "sobre",
            "kwargs": {
                "title": "Sobre o GabaritoAC",
                "slug": "sobre",
                "search_description": "Conheça o GabaritoAC, o maior portal de notícias sobre educação, concursos e processos seletivos do estado do Acre.",
                "corpo": SOBRE_BODY,
            },
        })

        self._create_page(home, ContatoPage, {
            "slug": "contato",
            "kwargs": {
                "title": "Contato",
                "slug": "contato",
                "search_description": "Entre em contato com o GabaritoAC. Tire dúvidas, sugestões ou divulgue seu edital.",
                "dpo_email": "dpo@gabaritoac.com.br",
                "corpo": CONTATO_BODY,
            },
        })

        self._create_page(home, PoliticaPrivacidadePage, {
            "slug": "privacidade",
            "kwargs": {
                "title": "Política de Privacidade",
                "slug": "privacidade",
                "search_description": "Política de Privacidade do GabaritoAC. Saiba como tratamos seus dados pessoais conforme a LGPD.",
                "corpo": PRIVACIDADE_BODY,
            },
        })

        self.stdout.write(self.style.SUCCESS("Concluído!"))
