const btnSwitch = document.querySelector('#switch');

btnSwitch.addEventListener('click', () => {
	document.body.classList.toggle('dark');
	btnSwitch.classList.toggle('active');
});

const btnDelete = document.querySelectorAll('.btn-delete')

if (btnDelete) {
	const btnArray = Array.from(btnDelete);
	btnArray.forEach(btn) => {
		btn.addEventListener('click', (e) => {
			if(!confirm('¿Estas seguro que desea eliminarlo?')) {
				e.preventDefault();
			}
		});
	};
} 