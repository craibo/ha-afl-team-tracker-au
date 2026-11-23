var j=globalThis,B=j.ShadowRoot&&(j.ShadyCSS===void 0||j.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,ne=Symbol(),fe=new WeakMap,T=class{constructor(e,t,n){if(this._$cssResult$=!0,n!==ne)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(B&&e===void 0){let n=t!==void 0&&t.length===1;n&&(e=fe.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),n&&fe.set(t,e))}return e}toString(){return this.cssText}},ge=r=>new T(typeof r=="string"?r:r+"",void 0,ne),P=(r,...e)=>{let t=r.length===1?r[0]:e.reduce((n,s,i)=>n+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+r[i+1],r[0]);return new T(t,r,ne)},_e=(r,e)=>{if(B)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let n=document.createElement("style"),s=j.litNonce;s!==void 0&&n.setAttribute("nonce",s),n.textContent=t.cssText,r.appendChild(n)}},re=B?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(let n of e.cssRules)t+=n.cssText;return ge(t)})(r):r;var{is:et,defineProperty:tt,getOwnPropertyDescriptor:nt,getOwnPropertyNames:rt,getOwnPropertySymbols:st,getPrototypeOf:it}=Object,F=globalThis,ye=F.trustedTypes,ot=ye?ye.emptyScript:"",at=F.reactiveElementPolyfillSupport,L=(r,e)=>r,se={toAttribute(r,e){switch(e){case Boolean:r=r?ot:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},ve=(r,e)=>!et(r,e),$e={attribute:!0,type:String,converter:se,reflect:!1,useDefault:!1,hasChanged:ve};Symbol.metadata??=Symbol("metadata"),F.litPropertyMetadata??=new WeakMap;var g=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=$e){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let n=Symbol(),s=this.getPropertyDescriptor(e,n,t);s!==void 0&&tt(this.prototype,e,s)}}static getPropertyDescriptor(e,t,n){let{get:s,set:i}=nt(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:s,set(o){let d=s?.call(this);i?.call(this,o),this.requestUpdate(e,d,n)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??$e}static _$Ei(){if(this.hasOwnProperty(L("elementProperties")))return;let e=it(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(L("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(L("properties"))){let t=this.properties,n=[...rt(t),...st(t)];for(let s of n)this.createProperty(s,t[s])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[n,s]of t)this.elementProperties.set(n,s)}this._$Eh=new Map;for(let[t,n]of this.elementProperties){let s=this._$Eu(t,n);s!==void 0&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let n=new Set(e.flat(1/0).reverse());for(let s of n)t.unshift(re(s))}else e!==void 0&&t.push(re(e));return t}static _$Eu(e,t){let n=t.attribute;return n===!1?void 0:typeof n=="string"?n:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let n of t.keys())this.hasOwnProperty(n)&&(e.set(n,this[n]),delete this[n]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return _e(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,n){this._$AK(e,n)}_$ET(e,t){let n=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,n);if(s!==void 0&&n.reflect===!0){let i=(n.converter?.toAttribute!==void 0?n.converter:se).toAttribute(t,n.type);this._$Em=e,i==null?this.removeAttribute(s):this.setAttribute(s,i),this._$Em=null}}_$AK(e,t){let n=this.constructor,s=n._$Eh.get(e);if(s!==void 0&&this._$Em!==s){let i=n.getPropertyOptions(s),o=typeof i.converter=="function"?{fromAttribute:i.converter}:i.converter?.fromAttribute!==void 0?i.converter:se;this._$Em=s;let d=o.fromAttribute(t,i.type);this[s]=d??this._$Ej?.get(s)??d,this._$Em=null}}requestUpdate(e,t,n,s=!1,i){if(e!==void 0){let o=this.constructor;if(s===!1&&(i=this[e]),n??=o.getPropertyOptions(e),!((n.hasChanged??ve)(i,t)||n.useDefault&&n.reflect&&i===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,n))))return;this.C(e,t,n)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:n,reflect:s,wrapped:i},o){n&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,o??t??this[e]),i!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||n||(t=void 0),this._$AL.set(e,t)),s===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[s,i]of this._$Ep)this[s]=i;this._$Ep=void 0}let n=this.constructor.elementProperties;if(n.size>0)for(let[s,i]of n){let{wrapped:o}=i,d=this[s];o!==!0||this._$AL.has(s)||d===void 0||this.C(s,void 0,i,d)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(n=>n.hostUpdate?.()),this.update(t)):this._$EM()}catch(n){throw e=!1,this._$EM(),n}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};g.elementStyles=[],g.shadowRootOptions={mode:"open"},g[L("elementProperties")]=new Map,g[L("finalized")]=new Map,at?.({ReactiveElement:g}),(F.reactiveElementVersions??=[]).push("2.1.2");var he=globalThis,be=r=>r,W=he.trustedTypes,we=W?W.createPolicy("lit-html",{createHTML:r=>r}):void 0,Se="$lit$",y=`lit$${Math.random().toFixed(9).slice(2)}$`,Te="?"+y,ct=`<${Te}>`,x=document,U=()=>x.createComment(""),H=r=>r===null||typeof r!="object"&&typeof r!="function",ue=Array.isArray,lt=r=>ue(r)||typeof r?.[Symbol.iterator]=="function",ie=`[ 	
\f\r]`,R=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,xe=/-->/g,Ee=/>/g,b=RegExp(`>|${ie}(?:([^\\s"'>=/]+)(${ie}*=${ie}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ke=/'/g,Ce=/"/g,Pe=/^(?:script|style|textarea|title)$/i,pe=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),l=pe(1),Mt=pe(2),Ot=pe(3),E=Symbol.for("lit-noChange"),h=Symbol.for("lit-nothing"),Ae=new WeakMap,w=x.createTreeWalker(x,129);function Le(r,e){if(!ue(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return we!==void 0?we.createHTML(e):e}var dt=(r,e)=>{let t=r.length-1,n=[],s,i=e===2?"<svg>":e===3?"<math>":"",o=R;for(let d=0;d<t;d++){let a=r[d],u,p,c=-1,f=0;for(;f<a.length&&(o.lastIndex=f,p=o.exec(a),p!==null);)f=o.lastIndex,o===R?p[1]==="!--"?o=xe:p[1]!==void 0?o=Ee:p[2]!==void 0?(Pe.test(p[2])&&(s=RegExp("</"+p[2],"g")),o=b):p[3]!==void 0&&(o=b):o===b?p[0]===">"?(o=s??R,c=-1):p[1]===void 0?c=-2:(c=o.lastIndex-p[2].length,u=p[1],o=p[3]===void 0?b:p[3]==='"'?Ce:ke):o===Ce||o===ke?o=b:o===xe||o===Ee?o=R:(o=b,s=void 0);let _=o===b&&r[d+1].startsWith("/>")?" ":"";i+=o===R?a+ct:c>=0?(n.push(u),a.slice(0,c)+Se+a.slice(c)+y+_):a+y+(c===-2?d:_)}return[Le(r,i+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),n]},M=class r{constructor({strings:e,_$litType$:t},n){let s;this.parts=[];let i=0,o=0,d=e.length-1,a=this.parts,[u,p]=dt(e,t);if(this.el=r.createElement(u,n),w.currentNode=this.el.content,t===2||t===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(s=w.nextNode())!==null&&a.length<d;){if(s.nodeType===1){if(s.hasAttributes())for(let c of s.getAttributeNames())if(c.endsWith(Se)){let f=p[o++],_=s.getAttribute(c).split(y),I=/([.?@])?(.*)/.exec(f);a.push({type:1,index:i,name:I[2],strings:_,ctor:I[1]==="."?ae:I[1]==="?"?ce:I[1]==="@"?le:A}),s.removeAttribute(c)}else c.startsWith(y)&&(a.push({type:6,index:i}),s.removeAttribute(c));if(Pe.test(s.tagName)){let c=s.textContent.split(y),f=c.length-1;if(f>0){s.textContent=W?W.emptyScript:"";for(let _=0;_<f;_++)s.append(c[_],U()),w.nextNode(),a.push({type:2,index:++i});s.append(c[f],U())}}}else if(s.nodeType===8)if(s.data===Te)a.push({type:2,index:i});else{let c=-1;for(;(c=s.data.indexOf(y,c+1))!==-1;)a.push({type:7,index:i}),c+=y.length-1}i++}}static createElement(e,t){let n=x.createElement("template");return n.innerHTML=e,n}};function C(r,e,t=r,n){if(e===E)return e;let s=n!==void 0?t._$Co?.[n]:t._$Cl,i=H(e)?void 0:e._$litDirective$;return s?.constructor!==i&&(s?._$AO?.(!1),i===void 0?s=void 0:(s=new i(r),s._$AT(r,t,n)),n!==void 0?(t._$Co??=[])[n]=s:t._$Cl=s),s!==void 0&&(e=C(r,s._$AS(r,e.values),s,n)),e}var oe=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:n}=this._$AD,s=(e?.creationScope??x).importNode(t,!0);w.currentNode=s;let i=w.nextNode(),o=0,d=0,a=n[0];for(;a!==void 0;){if(o===a.index){let u;a.type===2?u=new O(i,i.nextSibling,this,e):a.type===1?u=new a.ctor(i,a.name,a.strings,this,e):a.type===6&&(u=new de(i,this,e)),this._$AV.push(u),a=n[++d]}o!==a?.index&&(i=w.nextNode(),o++)}return w.currentNode=x,s}p(e){let t=0;for(let n of this._$AV)n!==void 0&&(n.strings!==void 0?(n._$AI(e,n,t),t+=n.strings.length-2):n._$AI(e[t])),t++}},O=class r{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,n,s){this.type=2,this._$AH=h,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=n,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=C(this,e,t),H(e)?e===h||e==null||e===""?(this._$AH!==h&&this._$AR(),this._$AH=h):e!==this._$AH&&e!==E&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):lt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==h&&H(this._$AH)?this._$AA.nextSibling.data=e:this.T(x.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:n}=e,s=typeof n=="number"?this._$AC(e):(n.el===void 0&&(n.el=M.createElement(Le(n.h,n.h[0]),this.options)),n);if(this._$AH?._$AD===s)this._$AH.p(t);else{let i=new oe(s,this),o=i.u(this.options);i.p(t),this.T(o),this._$AH=i}}_$AC(e){let t=Ae.get(e.strings);return t===void 0&&Ae.set(e.strings,t=new M(e)),t}k(e){ue(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,n,s=0;for(let i of e)s===t.length?t.push(n=new r(this.O(U()),this.O(U()),this,this.options)):n=t[s],n._$AI(i),s++;s<t.length&&(this._$AR(n&&n._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let n=be(e).nextSibling;be(e).remove(),e=n}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},A=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,n,s,i){this.type=1,this._$AH=h,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=i,n.length>2||n[0]!==""||n[1]!==""?(this._$AH=Array(n.length-1).fill(new String),this.strings=n):this._$AH=h}_$AI(e,t=this,n,s){let i=this.strings,o=!1;if(i===void 0)e=C(this,e,t,0),o=!H(e)||e!==this._$AH&&e!==E,o&&(this._$AH=e);else{let d=e,a,u;for(e=i[0],a=0;a<i.length-1;a++)u=C(this,d[n+a],t,a),u===E&&(u=this._$AH[a]),o||=!H(u)||u!==this._$AH[a],u===h?e=h:e!==h&&(e+=(u??"")+i[a+1]),this._$AH[a]=u}o&&!s&&this.j(e)}j(e){e===h?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},ae=class extends A{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===h?void 0:e}},ce=class extends A{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==h)}},le=class extends A{constructor(e,t,n,s,i){super(e,t,n,s,i),this.type=5}_$AI(e,t=this){if((e=C(this,e,t,0)??h)===E)return;let n=this._$AH,s=e===h&&n!==h||e.capture!==n.capture||e.once!==n.once||e.passive!==n.passive,i=e!==h&&(n===h||s);s&&this.element.removeEventListener(this.name,this,n),i&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},de=class{constructor(e,t,n){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=n}get _$AU(){return this._$AM._$AU}_$AI(e){C(this,e)}};var ht=he.litHtmlPolyfillSupport;ht?.(M,O),(he.litHtmlVersions??=[]).push("3.3.3");var Re=(r,e,t)=>{let n=t?.renderBefore??e,s=n._$litPart$;if(s===void 0){let i=t?.renderBefore??null;n._$litPart$=s=new O(e.insertBefore(U(),i),i,void 0,t??{})}return s._$AI(r),s};var me=globalThis,m=class extends g{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Re(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return E}};m._$litElement$=!0,m.finalized=!0,me.litElementHydrateSupport?.({LitElement:m});var ut=me.litElementPolyfillSupport;ut?.({LitElement:m});(me.litElementVersions??=[]).push("4.2.2");var pt=[{name:"entity",selector:{entity:{domain:"sensor",integration:"afl_team_tracker"}}}],X=class extends m{constructor(){super(...arguments);this._label=t=>t.name==="entity"?"Game entity":t.name}setConfig(t){this._config=t}set hass(t){this._hass=t}_changed(t){let n={...this._config,...t.detail.value};this._config=n,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:n},bubbles:!0,composed:!0}))}render(){if(this._config)return l`<ha-form
      .hass=${this._hass}
      .data=${this._config}
      .schema=${pt}
      .computeLabel=${this._label}
      @value-changed=${this._changed}
    ></ha-form>`}};X.properties={_config:{state:!0},_hass:{state:!0}};customElements.get("afl-tracker-game-card-editor")||customElements.define("afl-tracker-game-card-editor",X);var mt=/^sensor\..*(current|next|previous)_game/;function q(r){return r?Object.keys(r).find(e=>mt.test(e))??"":""}function Ue(r,e,t){return!r||!e?!0:r[t]!==e[t]}function He(r,e,t){return!r||!e?!0:t.some(n=>r[n]!==e[n])}var ft={mode:"empty",home:{name:""},away:{name:""},headline:"No game"},N=()=>({...ft,home:{name:""},away:{name:""}}),$=r=>typeof r=="string"&&r!==""?r:void 0,Me=r=>typeof r=="number"&&Number.isFinite(r)?r:void 0,gt=new Set(["www.afl.com.au","afl.com.au"]);function k(r){if(!(typeof r!="string"||r.trim()===""))try{let e=new URL(r);return e.protocol!=="https:"||!gt.has(e.hostname)||e.username!==""||e.password!==""||e.port!==""?void 0:e.href}catch{return}}var Oe=k;function De(r,e){return`Open the match: ${r} v ${e}`}var ze=r=>`Open ${r}`,Ie=()=>"Open the match";function K(r,e){let t=typeof r=="string"?r.trim():"";return t!==""?t:e.trim().slice(0,3).toUpperCase()}var Ne=r=>typeof r=="string"&&r.trim()!==""?r.trim():void 0,_t={one:"st",two:"nd",few:"rd",other:"th"},yt=r=>typeof r=="number"&&Number.isInteger(r)&&r>0?r:void 0;function $t(r,e){if(typeof e!="string"||!/^en(?:$|[-_])/i.test(e))return`#${r}`;let t;try{t=new Intl.PluralRules(e,{type:"ordinal"})}catch{t=new Intl.PluralRules("en",{type:"ordinal"})}return`${r}${_t[t.select(r)]??"th"}`}function Y(r,e){let t=yt(r);return t===void 0?{}:{rank:t,rankLabel:$t(t,e)}}function Ve(r,e,t){let n=$(r);if(!n)return{headline:"TBC"};let s=new Date(n);if(Number.isNaN(s.getTime()))return{headline:n};try{return{dateLine:new Intl.DateTimeFormat(e,{weekday:"short",day:"numeric",month:"short",timeZone:t}).format(s),headline:new Intl.DateTimeFormat(e,{hour:"2-digit",minute:"2-digit",timeZone:t}).format(s)}}catch{return{headline:n}}}function S(r,e,t){try{if(!r||r.state==="unavailable"||r.state==="unknown")return N();let n=r.attributes;if(!n||typeof n!="object")return N();let s=$(n.period),i=$(n.home_team),o=$(n.away_team);if(!s||!i||!o)return N();let d=n.logos&&typeof n.logos=="object"?n.logos:{},a=Me(n.home_score),u=Me(n.away_score),p={name:i,abbr:K(n.home_abbr,i),logo:$(d.home),score:a,scoreDetail:$(n.home_score_detail),...Y(n.home_rank,e),url:Oe(n.home_team_url)},c={name:o,abbr:K(n.away_abbr,o),logo:$(d.away),score:u,scoreDetail:$(n.away_score_detail),...Y(n.away_rank,e),url:Oe(n.away_team_url)},f=`${a??"-"} \u2013 ${u??"-"}`;switch(s){case"Upcoming":return{mode:"upcoming",home:p,away:c,...Ve(n.kickoff,e,t),venue:Ne(n.venue),matchUrl:k(n.match_url)};case"Postponed":case"Cancelled":return{mode:"upcoming",home:p,away:c,...Ve(n.kickoff,e,t),badge:s,venue:Ne(n.venue),matchUrl:k(n.match_url)};case"Live":return{mode:"live",home:p,away:c,headline:f,badge:"Live",matchUrl:k(n.match_url)};case"Result":return{mode:"final",home:p,away:c,headline:f,badge:"Full time",matchUrl:k(n.match_url)};default:return N()}}catch{return N()}}var Be=r=>`Open the match against ${r}`,V=5,je=/_(?:current_game|next_game|previous_game_[1-5])$/,vt=/^([WLD]) \d+–\d+$/,v=r=>typeof r=="string"&&r!==""?r:void 0;function Fe(r){if(typeof r!="string"||!je.test(r))return;let e=r.replace(je,"");return{current:`${e}_current_game`,next:`${e}_next_game`,previous:[1,2,3,4,5].map(t=>`${e}_previous_game_${t}`)}}function We(r){let e=Array.isArray(r?.previous)?r.previous.filter(s=>typeof s=="string"&&s!==""):[];if(!(!!r&&typeof r=="object"&&(typeof r.current=="string"||typeof r.next=="string"||Array.isArray(r.previous))))throw new Error("afl-tracker-team-card: configure at least 'next', 'current' or 'previous'");let n={...r,previous:e.slice(0,V)};return typeof n.title!="string"&&delete n.title,typeof n.show_header!="boolean"&&delete n.show_header,n}var bt=/(?:^|\s+)(?:current game|next game|previous game [1-5])\s*$/i;function wt(r){if(!r||typeof r!="object")return[];let e=Array.isArray(r.previous)?r.previous.slice(0,V):[];return[r.next,r.current,...e].filter(t=>typeof t=="string"&&t!=="")}function xt(r,e){try{let t=wt(e),n=s=>r&&typeof r=="object"?r[s]:void 0;for(let s of t){let i=n(s)?.attributes;if(!i||typeof i!="object")continue;let o=i.home_away==="home"?v(i.home_team):i.home_away==="away"?v(i.away_team):void 0;if(o)return o}for(let s of t){let i=n(s)?.attributes,o=i&&typeof i=="object"?v(i.friendly_name):void 0;if(!o)continue;let d=o.replace(bt,"").trim();return d!==""?d:void 0}}catch{}}function Et(r){return[r.current,r.next,...(r.previous??[]).slice(0,V)].filter(e=>typeof e=="string"&&e!=="")}function kt(r,e,t){let n=v(r);if(!n)return"\u2013";let s=new Date(n);if(Number.isNaN(s.getTime()))return n;try{return new Intl.DateTimeFormat(e,{day:"numeric",month:"short",timeZone:t}).format(s)}catch{return n}}function Ct(r,e,t){try{if(!r||r.state==="unknown"||r.state==="unavailable")return;let n=r.attributes;if(!n||typeof n!="object")return;let s=v(n.opposition);if(!s)return;let i=typeof r.state=="string"?r.state:"",o=vt.exec(i),d=o?{W:"win",L:"loss",D:"draw"}[o[1]]:"unknown",a=v(n.home_score_detail),u=v(n.away_score_detail),p=a&&u?n.home_away==="away"?`${u} \u2013 ${a}`:`${a} \u2013 ${u}`:void 0;return{date:kt(n.kickoff,e,t),opposition:s,location:typeof n.venue=="string"&&n.venue.trim()!==""?n.venue.trim():void 0,...Y(n.home_away==="home"?n.away_rank:n.home_away==="away"?n.home_rank:void 0,e),matchUrl:k(n.match_url),score:i||"Result unavailable",scoreDetail:p,outcome:d}}catch{return}}function Xe(r,e,t,n){let s=c=>c?r[c]:void 0,i=S(s(e.current),t,n),o=S(s(e.next),t,n),d=i.mode==="live"?i:o.mode==="upcoming"?o:S(void 0,t,n),a=i.mode==="live"?e.current:e.next??e.current,u=(e.previous??[]).slice(0,V).map(c=>Ct(s(c),t,n)).filter(c=>c!==void 0),p=e.show_header===!1?void 0:v(e.title)??xt(r,e);return{top:d,previous:u,heading:p,moreInfoEntity:a}}function qe(r,e,t,n,s){return!r||e?!0:t?He(n,s,Et(r)):!0}function Ke(r){return 2+Math.min(V,r)}function Ye(r){let e=Fe(q(r));return e?{type:"custom:afl-tracker-team-card",...e}:{type:"custom:afl-tracker-team-card",next:""}}function Ge(r,e,t,n,s){let i={type:t??"custom:afl-tracker-team-card"};e&&(i.title=e),s===!1&&(i.show_header=!1);let o=r?Fe(r):void 0;return o?(i.current=o.current,i.next=o.next,i.previous=[...o.previous]):i.next=r??"",i}var At=[{name:"entity",selector:{entity:{domain:"sensor",integration:"afl_team_tracker"}}},{name:"title",selector:{text:{}}},{name:"show_header",selector:{boolean:{}}}],St={entity:"Any game sensor for the team",title:"Header title (optional, defaults to the team name)",show_header:"Show header"},G=class extends m{constructor(){super(...arguments);this._helper=t=>t.name==="entity"?"Other sensors are filled in automatically. Set them individually in YAML if needed.":t.name==="show_header"?"Show the followed team's name (or your title) at the top of the card.":void 0;this._label=t=>St[t.name]??t.name}setConfig(t){this._config=t}set hass(t){this._hass=t}_changed(t){let n=t.detail?.value??{},s=typeof n.entity=="string"?n.entity:"",i=typeof n.title=="string"&&n.title!==""?n.title:void 0,o=n.show_header===!1?!1:void 0,d=Ge(s,i,this._config?.type,this._config,o);this._config=d,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:d},bubbles:!0,composed:!0}))}render(){if(!this._config)return;let t={entity:this._config.next||this._config.current||this._config.previous?.[0]||"",title:this._config.title??"",show_header:this._config.show_header!==!1};return l`<ha-form
      .hass=${this._hass}
      .data=${t}
      .schema=${At}
      .computeLabel=${this._label}
      .computeHelper=${this._helper}
      @value-changed=${this._changed}
    ></ha-form>`}};G.properties={_config:{state:!0},_hass:{state:!0}};customElements.get("afl-tracker-team-card-editor")||customElements.define("afl-tracker-team-card-editor",G);function J(r,e){r.customCards=r.customCards||[],r.customCards.some(t=>t.type===e.type)||r.customCards.push(e)}function Q(r,e=500){let t,n,s=!1,i=()=>{t!==void 0&&clearTimeout(t),t=void 0,n=void 0};return{start(o){o.button!==void 0&&o.button!==0||(i(),s=!1,n=o,t=setTimeout(()=>{t=void 0,n=void 0,s=!0,r()},e))},move(o){n&&Math.hypot(o.clientX-n.clientX,o.clientY-n.clientY)>10&&i()},cancel:i,consumeFired(){let o=s;return s=!1,o}}}function Z(r,e){r.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:e},bubbles:!0,composed:!0}))}function Je(r){let e=K(r.abbr,r.name);return l`${r.logo?l`<img class="logo" src=${r.logo} alt="" />`:l`<div class="logo logo-badge" aria-hidden="true">${e}</div>`}
    <div class="name">
      ${r.name}${r.rankLabel?l` <span class="rank">${r.rankLabel}</span>`:h}
    </div>`}function Qe(r,e){return e&&r.url?l`<a
      class="team team-link"
      href=${r.url}
      target="_blank"
      rel="noopener noreferrer"
      aria-label=${ze(r.name)}
      >${Je(r)}</a
    >`:l`<div class="team">${Je(r)}</div>`}function Tt(r){return r.mode==="upcoming"||!r.home.scoreDetail||!r.away.scoreDetail?h:l`<div class="score-detail">${r.home.scoreDetail} – ${r.away.scoreDetail}</div>`}function Ze(r){return l`${r.dateLine?l`<div class="dateline">${r.dateLine}</div>`:h}
    <div class="headline">${r.headline}</div>
    ${Tt(r)}
    ${r.venue?l`<div class="venue">${r.venue}</div>`:h}
    ${r.badge?l`<div class="badge">${r.badge}</div>`:h}`}function Pt(r,e){return e&&r.matchUrl?l`<a
      class="centre centre-link"
      href=${r.matchUrl}
      target="_blank"
      rel="noopener noreferrer"
      aria-label=${Ie()}
      >${Ze(r)}</a
    >`:l`<div class="centre">${Ze(r)}</div>`}function ee(r,e={}){if(r.mode==="empty")return l`<div class="empty">${r.headline}</div>`;let t=e.linkMode==="parts",n=l`<div class="game ${r.mode}">
    <div class="row">
      ${Qe(r.home,t)} ${Pt(r,t)} ${Qe(r.away,t)}
    </div>
  </div>`;return t||!r.matchUrl||r.mode!=="live"&&r.mode!=="final"?n:l`<a
    class="game-link"
    href=${r.matchUrl}
    target="_blank"
    rel="noopener noreferrer"
    aria-label=${De(r.home.name,r.away.name)}
    >${n}</a
  >`}var te=P`
    ha-card {
      padding: 16px;
      color: var(--primary-text-color);
    }
    .row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    .team {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      min-width: 0;
    }
    .logo {
      width: 56px;
      height: 56px;
      object-fit: contain;
    }
    /* Club logos are drawn for light backgrounds: sit them on a light disc so
       dark crests stay legible in dark themes. */
    img.logo {
      box-sizing: border-box;
      padding: 5px;
      border-radius: 50%;
      background: #fff;
    }
    .logo-badge {
      display: flex;
      align-items: center;
      justify-content: center;
      box-sizing: border-box;
      border-radius: 50%;
      background: var(--secondary-background-color);
      color: var(--primary-text-color);
      border: 2px solid var(--divider-color);
      font-weight: 700;
      font-size: 1em;
      letter-spacing: 0.02em;
    }
    .score-detail {
      font-size: 0.8em;
      color: var(--secondary-text-color);
      white-space: nowrap;
    }
    .name {
      margin-top: 6px;
      font-weight: 500;
      max-width: 100%;
      overflow-wrap: anywhere;
    }
    .rank {
      font-size: 0.8em;
      font-weight: 400;
      color: var(--secondary-text-color);
      white-space: nowrap;
    }
    .centre {
      flex: 1;
      min-width: 0;
      text-align: center;
    }
    .headline {
      font-size: 1.4em;
      font-weight: 600;
    }
    .game.upcoming .headline {
      font-size: 1.15em;
      white-space: nowrap;
    }
    .dateline {
      font-size: 0.85em;
      color: var(--secondary-text-color);
      white-space: nowrap;
    }
    .venue {
      min-width: 0;
      max-width: 100%;
      font-size: 0.85em;
      color: var(--secondary-text-color);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .game-link,
    .prev-row a.prev-link {
      color: inherit;
      text-decoration: none;
      cursor: pointer;
      border-radius: 8px;
    }
    .game-link {
      display: block;
    }
    a.team-link,
    a.centre-link {
      color: inherit;
      text-decoration: none;
      cursor: pointer;
      border-radius: 8px;
    }
    a.centre-link {
      display: block;
    }
    a.team-link:hover,
    a.centre-link:hover,
    a.team-link:focus-visible,
    a.centre-link:focus-visible {
      background: var(--secondary-background-color);
    }
    a.team-link:focus-visible,
    a.centre-link:focus-visible {
      outline: 2px solid var(--primary-color);
      outline-offset: 2px;
    }
    .game-link:hover,
    .game-link:focus-visible,
    .prev-row a.prev-link:hover,
    .prev-row a.prev-link:focus-visible {
      background: var(--secondary-background-color);
    }
    .badge {
      display: inline-block;
      margin-top: 6px;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: 0.85em;
      background: var(--secondary-background-color);
      color: var(--secondary-text-color);
    }
    ha-card .game.live .badge {
      background: var(--error-color, #db4437);
      color: var(--text-primary-color, #fff);
    }
    ha-card .game.live .headline {
      color: var(--primary-color);
    }
    .empty {
      text-align: center;
      color: var(--secondary-text-color);
      padding: 8px;
    }
`;var D=class extends m{constructor(){super(...arguments);this._press=Q(()=>{let t=this._view()?.moreInfoEntity;t&&Z(this,t)})}disconnectedCallback(){super.disconnectedCallback(),this._press.cancel()}static getConfigElement(){return document.createElement("afl-tracker-team-card-editor")}static getStubConfig(t){return Ye(t?.states)}shouldUpdate(t){let n=t.get("_hass");return qe(this._config,t.has("_config"),t.has("_hass"),n?.states,this._hass?.states)}setConfig(t){this._config=We(t)}set hass(t){this._hass=t}getCardSize(){return Ke(this._view()?.previous.length??0)}_view(){if(!this._config)return;let t=this._hass;return Xe(t?.states??{},this._config,t?.locale?.language??"en",t?.config?.time_zone??"UTC")}render(){let t=this._view();return t?l`<ha-card
      @pointerdown=${n=>this._press.start(n)}
      @pointermove=${n=>this._press.move(n)}
      @pointerup=${()=>this._press.cancel()}
      @pointercancel=${()=>this._press.cancel()}
      @pointerleave=${()=>this._press.cancel()}
      @contextmenu=${n=>n.preventDefault()}
      @click=${n=>{this._press.consumeFired()&&(n.preventDefault(),n.stopPropagation())}}
    >
      ${t.heading?l`<div class="heading">${t.heading}</div>`:h}
      ${ee(t.top,{linkMode:"parts"})}
      <hr class="divider" />
      ${t.previous.length===0?l`<div class="none">No previous games</div>`:l`<ul class="previous">
            ${t.previous.map(n=>{let s=l`<span class="date">${n.date}</span>
                <span class="opp"
                  >${n.opposition}${n.rankLabel?l` <span class="rank">${n.rankLabel}</span>`:h}${n.location?l` <span class="loc">(${n.location})</span>`:h}</span
                >
                <span class="score ${n.outcome}" title=${n.scoreDetail??h}
                  >${n.score}</span
                >`;return l`<li class="prev-row">
                ${n.matchUrl?l`<a
                      class="prev-link"
                      href=${n.matchUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label=${Be(n.opposition)}
                      >${s}</a
                    >`:s}
              </li>`})}
          </ul>`}
    </ha-card>`:h}};D.properties={_config:{state:!0},_hass:{state:!0}},D.styles=[te,P`
      .heading {
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 8px;
      }
      .divider {
        border: 0;
        border-top: 1px solid var(--divider-color);
        margin: 12px 0;
      }
      .previous {
        list-style: none;
        margin: 0;
        padding: 0;
      }
      .prev-row {
        display: flex;
        gap: 8px;
        align-items: baseline;
        padding: 3px 0;
        font-size: 0.9em;
      }
      .prev-row a.prev-link {
        display: flex;
        flex: 1;
        min-width: 0;
        gap: 8px;
        align-items: baseline;
        margin: -3px -4px;
        padding: 3px 4px;
      }
      .date {
        flex: 0 0 auto;
        min-width: 5.5em;
        color: var(--secondary-text-color);
      }
      .opp {
        flex: 1;
        min-width: 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .loc,
      .prev-row .rank {
        color: var(--secondary-text-color);
      }
      .prev-row .rank {
        font-size: inherit;
      }
      .score {
        flex: 0 0 auto;
        font-weight: 600;
      }
      .score.win {
        color: var(--success-color);
      }
      .score.loss {
        color: var(--error-color);
      }
      .score.draw {
        color: var(--warning-color);
      }
      .score.unknown {
        color: var(--secondary-text-color);
      }
      .none {
        text-align: center;
        color: var(--secondary-text-color);
      }
    `];customElements.get("afl-tracker-team-card")||customElements.define("afl-tracker-team-card",D);J(window,{type:"afl-tracker-team-card",name:"AFL Tracker Team Card",description:"Current or next game plus the previous five results for one team"});var z=class extends m{constructor(){super(...arguments);this._press=Q(()=>{this._config&&Z(this,this._config.entity)})}disconnectedCallback(){super.disconnectedCallback(),this._press.cancel()}static getConfigElement(){return document.createElement("afl-tracker-game-card-editor")}static getStubConfig(t){return{type:"custom:afl-tracker-game-card",entity:q(t?.states)}}shouldUpdate(t){if(!this._config||t.has("_config"))return!0;if(t.has("_hass")){let n=t.get("_hass");return Ue(n?.states,this._hass?.states,this._config.entity)}return!0}setConfig(t){if(!t||typeof t.entity!="string"||!t.entity)throw new Error("afl-tracker-game-card: 'entity' is required");this._config=t}set hass(t){this._hass=t}getCardSize(){return 2}_view(){let t=this._hass,n=t&&this._config?t.states[this._config.entity]:void 0;return S(n,t?.locale?.language??"en",t?.config?.time_zone??"UTC")}render(){return this._config?l`<ha-card
      @pointerdown=${t=>this._press.start(t)}
      @pointermove=${t=>this._press.move(t)}
      @pointerup=${()=>this._press.cancel()}
      @pointercancel=${()=>this._press.cancel()}
      @pointerleave=${()=>this._press.cancel()}
      @contextmenu=${t=>t.preventDefault()}
      @click=${t=>{this._press.consumeFired()&&(t.preventDefault(),t.stopPropagation())}}
      >${ee(this._view())}</ha-card
    >`:h}};z.properties={_config:{state:!0},_hass:{state:!0}},z.styles=te;customElements.get("afl-tracker-game-card")||customElements.define("afl-tracker-game-card",z);J(window,{type:"afl-tracker-game-card",name:"AFL Tracker Game Card",description:"Shows an AFL game: start time, live score or final result."});export{z as AflTrackerGameCard};
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
