<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta http-equiv="X-UA-Compatible" content="IE=edge" />
	<?php echo $this->Html->charset(); ?>
	<title>
		<?php echo $title_for_layout, ' - MISP'; ?>
	</title>
	<?php
		echo $this->Html->meta('icon');
// 		echo $this->Html->css('cake.generic');
		echo $this->Html->css('roboto');
		echo $this->Html->css('bootstrap'); // see http://twitter.github.io/bootstrap/base-css.html
		echo $this->Html->css('datepicker');
		echo $this->Html->css('bootstrap-timepicker');
		echo $this->Html->css('bootstrap-colorpicker.min');
		echo $this->Html->css('main');
		echo $this->Html->css('print', 'stylesheet', array('media' => 'print'));

		// FIXME chri: re-add print stylesheet
		//echo $this->Html->css(array('print'), 'stylesheet', array('media' => 'print'));

		echo $this->fetch('meta');
		echo $this->fetch('css');
		echo $this->fetch('script');

		echo $this->Html->script('jquery-2.1.0.min'); // Include jQuery library
	?>

<!--?php echo $scripts_for_layout; ?-->
</head>
<body>
	<div id="popover_form" class="ajax_popover_form"></div>
	<div id="confirmation_box" class="confirmation_box"></div>
	<div id="gray_out" class="gray_out"></div>
		<div id="container">
			<?php echo $this->element('global_menu');
			    $padding_top = 10;
			    if ($debugMode == 'debugOff') $padding_top = 50;
			?>
		<div class="container-fluid <?php echo $debugMode; ?>" style="padding-top:<?php echo $padding_top; ?>px;width:98%;">
			<?php
				$has_flash = false;
			    $flash = array();
			    $flash[] = $this->Session->flash('email');
			    $flash[] = $this->Session->flash();
			    $flash[] = $this->Session->flash('gpg');
			    $flash[] = $this->Session->flash('error');
			    $flash[] = $this->Session->flash('auth');
			    foreach ($flash as $f) {
					if ($f) {
						echo $f;
						$has_flash = true;
						continue;
					}
	            }
			?>
		</div>
		<?php
			$topGap = 50;
			if (Configure::read('debug') != 0) {
				$topGap = 10;
			} else {
	 			if ($has_flash) $topGap += 50;
	 		}
		?>
		<div style="padding-top:<?php echo $topGap; ?>px !important;">	
			<?php echo $this->fetch('content'); ?>
		</div>
	</div>
	<?php
	echo $this->element('footer');
	echo $this->element('sql_dump');
	echo $this->Html->script('bootstrap');
	// echo $this->Html->script('bootstrap.min');
	echo $this->Html->script('bootstrap-timepicker');
	echo $this->Html->script('bootstrap-datepicker');
	echo $this->Html->script('bootstrap-colorpicker.min');
	echo $this->Html->script('main');
	echo $this->Html->script('ajaxification');
	?>
	<div id = "ajax_success_container" class="ajax_container">
		<div id="ajax_success" class="ajax_result ajax_success"></div>
	</div>
	<div id = "ajax_fail_container" class="ajax_container">
		<div id="ajax_fail" class="ajax_result ajax_fail"></div>
	</div>
	<div class="loading">
		<div class="spinner"></div>
		<div class="loadingText">Loading</div>
	</div>
	<?php
		if ($debugMode == 'debugOff'):
	?>
	<script type="text/javascript">
		$(window).scroll(function(e) {
			$('.actions').css('left',-$(window).scrollLeft());
		});
	</script>
	<?php 
		endif;
	?>
</body>
</html>
