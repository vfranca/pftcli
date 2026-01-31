# pftcli

CLI acessível para automação de trading via integração com uma DLL de plataforma de mercado.

O **pftcli** permite interagir com uma DLL de trading instalada localmente, facilitando automação, testes, inspeção de estado e integração com outros sistemas via linha de comando.

> Projeto focado em simplicidade, acessibilidade em terminal e uso técnico por desenvolvedores.

---

## Características

- Interface de linha de comando (CLI)
- Saída textual amigável para leitores de tela (NVDA, JAWS, etc.)
- Foco em automação e integração
- Não utiliza gráficos ou interfaces visuais
- Projetado para uso em **Windows**

---

## 📦 Instalação

Via PyPI:

```bash
pip install pftcli
````

Ou usando Poetry:

```bash
poetry add pftcli
```

---

## Uso básico

Após a instalação, os seguintes comandos ficam disponíveis:

```bash
pft --help
```

ou

```bash
pftcli --help
```

Exemplo:

```bash
pft status
```

*(Os comandos disponíveis dependem da implementação atual do CLI.)*

---

## Requisitos

* Python **3.13 ou superior**
* Sistema operacional **Windows**
* DLL da plataforma de trading devidamente instalada e licenciada no ambiente do usuário

---

## Aviso importante (Disclaimer)

Este projeto:

* **Não é afiliado, patrocinado ou endossado por qualquer empresa proprietária da plataforma ou da DLL utilizada**
* **Não distribui DLLs proprietárias**
* Depende de uma DLL instalada separadamente pelo usuário, sob licença válida

O usuário é inteiramente responsável por cumprir os termos de licença da plataforma e da DLL utilizada.

---

## Licença

Este projeto é distribuído sob a licença **GNU General Public License v3.0 ou posterior (GPL-3.0-or-later)**.

Você pode:

* Usar
* Estudar
* Modificar
* Redistribuir

Desde que qualquer redistribuição de versões modificadas também seja feita sob a GPL.

Consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes.

---

## Desenvolvimento

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/pftcli.git
cd pftcli
```

Instale dependências:

```bash
poetry install
```

Execute localmente:

```bash
poetry run pft --help
```

---

## Contribuições

Contribuições são bem-vindas.

* Abra issues para bugs ou sugestões
* Envie pull requests com descrições claras
* Priorize legibilidade, simplicidade e acessibilidade em terminal

---

## Status do projeto

🚧 **Em desenvolvimento (Alpha)**
A API e os comandos podem mudar sem aviso prévio.
