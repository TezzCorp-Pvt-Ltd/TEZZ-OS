.bss
g_buf:
  .zero 40960
.text
.text
.extern say
.extern say_str
.extern say_f
.extern say_multi
.extern len
.extern tn_strcmp
.extern memcpy
.extern malloc
.extern free
.extern input_i64
.extern input_line
.extern tn_fopen
.extern tn_fclose
.extern tn_fflush
.extern tn_fread
.extern tn_fwrite
.extern tn_fseek
.extern tn_ftell
.extern tn_file_size
.extern tn_read_file
.extern tn_write_file
.extern tn_read_line
.extern tn_read_bytes
.extern tn_write_line
.extern tn_io_err
.extern tn_io_eof
.extern tn_stdin
.extern tn_stdout
.extern tn_stderr
.extern tn_get_cwd
.extern tn_chdir
.extern tn_mkdir
.extern tn_rmdir
.extern tn_remove
.extern tn_rename
.extern tn_path_exists
.extern tn_path_is_dir
.extern tn_path_join
.extern tn_path_sep
.extern tn_path_basename
.extern tn_path_dirname
.extern tn_list_dir
.extern tn_list_dir_recursive
.extern tn_glob
.extern tn_path_normalize
.extern tn_path_normalize_opts
.extern tn_time_now
.extern tn_time_now_ms
.extern tn_time_now_ns
.extern tn_date_now
.extern tn_date_now_utc
.extern tn_sleep_ms
.extern tn_bit_popcnt
.extern tn_bit_clz
.extern tn_bit_ctz
.extern tn_bit_bswap
.extern tn_bit_rotl
.extern tn_bit_rotr
.extern tn_cpu_has_sse2
.extern tn_cpu_has_avx2
.extern tn_cpu_has_fma
.extern tn_cpu_has_neon
.extern tn_async_spawn
.extern tn_async_await
.extern tn_async_workers
.extern tn_async_pending
.extern tn_net_af_inet
.extern tn_net_af_inet6
.extern tn_net_sock_stream
.extern tn_net_sock_dgram
.extern tn_net_ipproto_tcp
.extern tn_net_ipproto_udp
.extern tn_net_init
.extern tn_net_cleanup
.extern tn_net_socket
.extern tn_net_close
.extern tn_net_connect
.extern tn_net_bind
.extern tn_net_listen
.extern tn_net_accept
.extern tn_net_send
.extern tn_net_recv
.extern tn_net_set_blocking
.extern tn_net_set_timeout
.extern tn_net_last_error
.extern tn_net_resolve
.extern tn_tls_connect
.extern tn_tls_connect_ex
.extern tn_tls_send
.extern tn_tls_recv
.extern tn_tls_close
.extern tn_tls_policy_reset
.extern tn_tls_policy_set_min
.extern tn_tls_policy_set_pin_sha256
.extern tn_tls_policy_set_handshake_timeout
.extern tn_tls_policy_get_min
.extern tn_tls_policy_get_handshake_timeout
.extern tn_tls_policy_pin_enabled
.extern tn_tzimage_decode_file
.extern tn_tzimage_free
.extern tn_simd_v4f_add
.extern tn_simd_v4f_sub
.extern tn_simd_v4f_mul
.extern tn_simd_v4f_dot
.extern tn_simd_v4i_add
.extern tn_simd_v4f_load
.extern tn_simd_v4f_store
.extern tn_simd_v4i_load
.extern tn_simd_v4i_store
.extern tn_gpu_has_backend
.extern tn_gpu_init
.extern tn_gpu_shutdown
.extern tn_gpu_device_count
.extern tn_gpu_set_device
.extern tn_gpu_alloc
.extern tn_gpu_free
.extern tn_gpu_memcpy_to_device
.extern tn_gpu_memcpy_to_host
.extern tn_gpu_memset
.extern tn_gpu_launch_1d
.extern tn_gpu_launch_dxil_1d
.extern tn_gpu_backend_name
.extern tn_gpu_supports_dxil
.extern tn_npu_has_backend
.extern tn_npu_init
.extern tn_npu_shutdown
.extern tn_npu_device_count
.extern tn_npu_set_device
.extern tn_npu_alloc
.extern tn_npu_free
.extern tn_npu_memcpy_to_device
.extern tn_npu_memcpy_to_host
.extern tn_npu_memset
.extern tn_npu_launch_1d
.extern tn_npu_launch_dxil_1d
.extern tn_npu_backend_name
.extern tn_npu_supports_dxil
.extern tn_npu_model_load
.extern tn_npu_model_free
.extern tn_npu_model_run_f64_1d
.extern args_count
.extern arg
.extern proc_run
.extern proc_out
.extern tn_http_download
.extern tn_os_name
.globl main
main:
  pushq %rbp
  movq %rsp, %rbp
  subq $80, %rsp
.Lmain_0:
  leaq g_buf(%rip), %rax
  movq %rax, -8(%rbp)
  movq $0, %rax
  movq %rax, -16(%rbp)
  movq -8(%rbp), %rax
  movq %rax, -40(%rbp)
  movq $65, %rax
  movq %rax, -64(%rbp)
  movq -40(%rbp), %rax
  movq -64(%rbp), %rcx
  movb %cl, (%rax)
  movq -16(%rbp), %rax
  movq %rbp, %rsp
  popq %rbp
  ret
  xor %eax, %eax
  movq %rbp, %rsp
  popq %rbp
  ret
