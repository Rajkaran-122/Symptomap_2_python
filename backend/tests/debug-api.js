
async function test() {
    try {
        const res = await fetch('http://localhost:8787/api/v1/outbreaks');
        console.log('Status:', res.status);
        const text = await res.text();
        console.log('Body:', text);
    } catch (e) {
        console.error(e);
    }
}

test();
